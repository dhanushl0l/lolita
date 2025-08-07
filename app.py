import argparse
import os
import subprocess
import logging
import platform
from openai import OpenAI
from config import  load_config_from_json

APP_VERSION = "0.0.1"
settings = load_config_from_json("config.json")

def main():
    log_level = os.getenv("LOG", settings.LOG_LEVEL).upper()
    logging.basicConfig(level=log_level)
    parser = argparse.ArgumentParser(description="Simple CLI app that reads messages")

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {APP_VERSION}',
        help="Show program's version number and exit"
    )

    parser.add_argument(
        '-m', '--message',
        type=str,
        required=True,
        help="Your message prompt"
    )

    args = parser.parse_args()
    print(f"lolita says: {get_message(args.message)}")

def get_message(prompt):
    client = OpenAI(
    api_key=settings.API_KEY,
    base_url=settings.BASE_URL,
    )    
    resp = client.chat.completions.create(
    model=settings.MODEL,
    messages=[
        {"role": "system", "content": "You’re helpful and concise."},
        {"role": "user", "content": prompt},
    ],
    )

    print(resp.choices[0].message.content)
    return prompt

def send_notification(title: str, message: str):
    system = platform.system()

    if system == "Linux":
        subprocess.run(["notify-send", title, message])
    elif system == "Darwin": 
        subprocess.run(["terminal-notifier", "-title", title, "-message", message])
    else:
        logging.error("Notification not supported on this OS")

if __name__ == "__main__":
    main()
