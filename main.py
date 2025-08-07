import argparse
import os
import sys
import logging
from openai import OpenAI
from config import load_config_from_json, login_tty

APP_VERSION = "0.0.1"
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
        print(f"lolita says\n{get_message(args.message)}")

def get_message(prompt):
    client = OpenAI(
        api_key=SETTINGS.API_KEY,
        base_url=SETTINGS.BASE_URL,
    )
    initial_resp = client.chat.completions.create(
        model=SETTINGS.MODEL,
        messages=[
            {"role": "system", "content": SETTINGS.ROLE},
            {"role": "user", "content": prompt},
        ],
        temperature=1.0,
        top_p=0.95,
        frequency_penalty=0.6,
    )
    initial_output = initial_resp.choices[0].message.content
    rewrite_prompt = f"{SETTINGS.REWRITE_PROMPT}\nText:\n{initial_output}"
    rewritten_resp = client.chat.completions.create(
        model=SETTINGS.MODEL,
        messages=[
            {
                "role": "system",
                "content": SETTINGS.REWRITE_PROMPT,
            },
            {"role": "user", "content": rewrite_prompt},
        ],
        temperature=1.2,
        top_p=0.98,
        frequency_penalty=0.8,
    )
    return (rewritten_resp.choices[0].message.content)


if __name__ == "__main__":
    main()
