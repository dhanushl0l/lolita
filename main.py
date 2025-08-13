import argparse
import os
import sys
import logging
from typing import Callable, Optional
from openai import OpenAI

from config import load_config_from_json, login_tty

NAME = "Lolita"
APP_VERSION = "0.0.4"
SETTINGS = load_config_from_json("config.json")

def main():
    log_level = os.getenv("LOG", SETTINGS.LOG_LEVEL).upper()
    logging.basicConfig(level=log_level)

    parser = argparse.ArgumentParser(description=f"{NAME} CLI")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
        help="Show program's version number and exit"
    )
    parser.add_argument(
        "-m", "--message",
        type=str,
        required=False,
        help="Your message prompt"
    )
    parser.add_argument(
        "-l", "--login",
        action="store_true",
        help="Trigger login mode"
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()
    if args.login:
        login_tty("config.json")
    if args.message:
        channel = print_token
        get_message(args.message, channel)

def get_message(prompt: str, channel: Optional[Callable[[str], None]] = None) -> None:
    client = OpenAI(api_key=SETTINGS.API_KEY, base_url=SETTINGS.BASE_URL)

    def send(msg: str):
        if channel:
            channel(msg)

    try:
        resp = client.chat.completions.create(
            model=SETTINGS.MODEL,
            messages=[
                {"role": "system", "content": SETTINGS.ROLE},
                {"role": "user", "content": prompt},
            ],
            temperature=SETTINGS.TEMPERATURE,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )
        text = (resp.choices[0].message.content or "").strip()
        rewrite_prompt = f"{SETTINGS.REWRITE_PROMPT}\nText:\n{text}"
        response_stream = client.chat.completions.create(
            model=SETTINGS.MODEL,
            messages=[
                {"role": "system", "content": SETTINGS.REWRITE_ROLE},
                {"role": "user", "content": rewrite_prompt},
            ],
            temperature=SETTINGS.TEMPERATURE_REWRITE,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stream=True,
        )
        full_message_parts = []
        for chunk in response_stream:
            token = getattr(chunk.choices[0].delta, "content", None)
            if token:
                send(token)              
                full_message_parts.append(token)
        final_text = "".join(full_message_parts) 
        print(final_text)
    except Exception as e:
        send(f"[Error] {str(e)}")

def print_token(token: str):
    print(token, end='', flush=True)

if __name__ == "__main__":
    main()