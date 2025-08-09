# Lolita CLI – AI Content Rewriter (Quillbot Bypass)

A command-line tool that generates human-like, undetectable text using GPT and rewriting strategies. Designed to achieve **0% AI detection score** on Quillbot’s AI Content Detector.

It also includes a web chatbot server powered by FastAPI for interactive AI conversations via a browser.


---

## Features

- Uses OpenAI API (GPT-3.5 / GPT-4 compatible with openai Python library) for prompt-to-response generation
- Rewrites output to bypass AI detection with multiple rewriting passes
- Configurable temperature settings for creativity and style control
- Supports logging configuration and role-based system messages
- Clean command-line interface for easy use
- Includes a web server powered by FastAPI for chatbot interaction

---

## Requirements

- Python 3.10 or higher
- OpenAI API key or compatible API key
- (Optional) Virtual environment for dependency management

---

## Configuration (`config.json`)

Instead of hardcoding, you can customize your settings via a JSON config file:

| Field Name            | Description                                                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------|
| `API_KEY`             | Your API key for Together AI or another compatible provider                                                 |
| `MODEL`               | The AI model to use for generation (e.g., `meta-llama/Llama-3.3-70B-Instruct-Turbo`)                        |
| `BASE_URL`            | The base URL of the API service endpoint (e.g., `https://api.together.xyz/v1`)                              |
| `ROLE`                | System prompt defining the AI’s role and behavior during the initial generation pass                        |
| `REWRITE_ROLE`        | Role/prompt that guides the rewriting pass to keep meaning while improving clarity                          |
| `REWRITE_PROMPT`      | Specific prompt template used during rewriting to improve grammar/flow without changing facts or numbers    |
| `TEMPERATURE`         | Temperature value controlling creativity for the initial generation pass                                    |
| `TEMPERATURE_REWRITE` | Temperature value controlling creativity for the rewrite pass                                               |
| `LOG_LEVEL`           | Logging verbosity level (e.g., `DEBUG`, `INFO`, `WARNING`, `CRITICAL`)                                      |


---

## Usage

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the CLI app with a message:
```bash
python main.py -m "your message"
```

Run the web server with FastAPI:
```bash
uvicorn web:app --reload
```

Configure API keys and settings interactively:
```bash
python main.py -l
```

---

## Notes

- The tool uses multiple rewriting passes to make text sound more human and avoid AI detection.
- Different temperatures per pass help control creativity vs. coherence.
- The web server offers a chat interface for real-time use.
