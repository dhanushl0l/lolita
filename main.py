import argparse
import os
import sys
import logging
from openai import OpenAI
from config import load_config_from_json, login_tty

APP_VERSION = "0.0.2"
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
        temperature=SETTINGS.TEMPERATURES[0],
        top_p=0.95,
        frequency_penalty=0.6,
    )
    initial_output = initial_resp.choices[0].message.content or ""
    rewritten_resp = rewrite_output(initial_output, client)


    return (rewritten_resp)

def rewrite_output(initial_output: str, client) -> str:
    text = initial_output

    for i in range(SETTINGS.NUM_PASSES):
        temperature = SETTINGS.TEMPERATURES[i % len(SETTINGS.TEMPERATURES)]
        rewrite_prompt = f"{SETTINGS.REWRITE_PROMPT}\nText:\n{text}"

        if i < SETTINGS.NUM_PASSES - 1:
            rewritten_resp = client.chat.completions.create(
                model=SETTINGS.MODEL,
                messages=[
                    {"role": "system", "content": SETTINGS.REWRITE_PROMPT},
                    {"role": "user", "content": rewrite_prompt},
                ],
                temperature=temperature,
                top_p=0.98,
                frequency_penalty=0.8,
            )
            text = rewritten_resp.choices[0].message.content.strip()
        else:
            response_stream = client.chat.completions.create(
                model=SETTINGS.MODEL,
                messages=[
                    {"role": "system", "content": SETTINGS.REWRITE_PROMPT},
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
                    print(token, end='', flush=True)
                    full_text += token
            print()  
            text = full_text.strip()
    return text

if __name__ == "__main__":
    main()
