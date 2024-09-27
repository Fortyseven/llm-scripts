#!/usr/bin/env python3

import sys
import json
import ollama
from rich import print

MODEL='llama3:latest'
#MODEL='phi3:latest'
PROMPT="""
You are a world class language translator. Translate the following text into English. Provide a simple pronunciation of the translated text for native English speakers, and any notes that might help give context for the translation. Respond ONLY with a properly JSON object (don't forget to escape any quotation marks) exactly like this: {\"src_language\":$LANGUAGE, \"translation\": $TRANSLATION, \"src_pronunciation\":$SRC_PRONUNCIATION,\"notes\":$NOTES}\n
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
        # 'temperature': 0.1,
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
