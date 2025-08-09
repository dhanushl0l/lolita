import argparse
import os
import sys
import logging
from openai import OpenAI, OpenAIError
from config import load_config_from_json, login_tty
from typing import Callable, Optional

APP_VERSION = "0.0.3"
SETTINGS = load_config_from_json("config.json")

def main():
    log_level = os.getenv("LOG", SETTINGS.LOG_LEVEL).upper()
    logging.basicConfig(level=log_level)

    parser = argparse.ArgumentParser(description="Lolita CLI")

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
        print("\n")

def get_message(prompt: str, channel: Optional[Callable[[str], None]] = None) -> str:
    client = OpenAI(
        api_key=SETTINGS.API_KEY,
        base_url=SETTINGS.BASE_URL,
    )
    text = ""
    passes = max(1, SETTINGS.NUM_PASSES)
    try:
        for i in range(passes):
            temperature = SETTINGS.TEMPERATURES[i % len(SETTINGS.TEMPERATURES)]
            if i == 0:
                rewrite_prompt = prompt
                system_message = SETTINGS.ROLE
            else:
                rewrite_prompt = f"{SETTINGS.REWRITE_PROMPT}\nText:\n{text}"
                system_message = SETTINGS.REWRITE_PROMPT
            is_last_pass = (i == passes - 1)
            if not is_last_pass:
                resp = client.chat.completions.create(
                    model=SETTINGS.MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": rewrite_prompt},
                    ],
                    temperature=temperature,
                    top_p=0.98,
                    frequency_penalty=0.8,
                )
                text = resp.choices[0].message.content or ""
            else:
                response_stream = client.chat.completions.create(
                    model=SETTINGS.MODEL,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": rewrite_prompt},
                    ],
                    temperature=temperature,
                    top_p=0.98,
                    frequency_penalty=0.8,
                    stream=True,
                )
                full_text = ""
                for chunk in response_stream:
                    token = getattr(chunk.choices[0].delta, "content", None)
                    if token:
                        if channel:
                            channel(token)
                        else:
                            print(token, end='', flush=True)
                        full_text += token
                if not channel:
                    print()
                text = full_text.strip()
    except OpenAIError as e:
        err_msg = f"[OpenAI API error] {str(e)}"
        if channel:
            channel(err_msg)
        else:
            print(err_msg)
        return err_msg
    return text


def print_token(token: str):
    print(token, end='', flush=True)

if __name__ == "__main__":
    main()