#!/usr/bin/env python3

import sys
import json
import ollama
from rich import print

MODEL='llama3.2:latest'
#MODEL='phi3:latest'
JSON_TEMPLATE = """
{
    "src_language":"$LANGUAGE",
    "translation": "$TRANSLATION",
    "src_pronunciation":"$SRC_PRONUNCIATION",
    "notes":"$NOTES"
}
"""

PROMPT=f"""
You are a world class language translator.

Translate the provided text into English. Translate the entire provided text.

If you cannot confidently and correctly translate the text, please respond with "I cannot confidently translate this text."

Do not invent or guess at a word's meaning. If you are unsure of a word's meaning, you may provide a literal translation of the word.

Provide a simple pronunciation of the translated text for native English speakers. If you cannot provide a pronunciation, leave this field blank.

Also add notes that might help give context for the translation.

Respond ONLY with a properly structured JSON object (don't forget to escape any quotation marks) exactly like this:

{JSON_TEMPLATE}\n
"""
args = " ".join(sys.argv[1:])

if len(args) == 0:
    print("Usage: translate.py <text>")
    sys.exit(1)

response = ollama.chat(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": PROMPT + args
        }
    ],
    # stream=True,
    options={
        'temperature': 0.2,
    },
)

try:
    response = response.get('message').get('content')

    # sanitize
    response = response.replace("”", "\"")
    response = response.replace("“", "\"")
    response = response.replace("’", "'")
    response = response.replace("‘", "'")

    response = json.loads(response)

    print(f"[red]LANG:[/red] {response['src_language']} -> [green]\"{response['translation']}\"[/green]")
    if response['src_pronunciation']:
        print(f"[purple]SRC_PRONUNCIATION: [bold]{response['src_pronunciation']}[/bold][/purple]")
    if response['notes']:
        print(f"[yellow]NOTES: {response['notes']}[/yellow]")

except Exception as e:
    print(f"ERROR: {e}\n\n{response}")
