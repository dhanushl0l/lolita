import argparse

APP_VERSION = "0.0.1"

def main():
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

    print(f"Ai says: {get_message(args.message)}")



def get_message(prompt):
    return prompt

if __name__ == "__main__":
    main()
