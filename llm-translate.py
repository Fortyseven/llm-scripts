#!/usr/bin/env python3

import sys
import json
from typing import Optional
import ollama
from rich import print
from pydantic import BaseModel
from rich.table import Table
from rich.console import Console

import argparse

DEBUG = False

args = None


# This script borrows the filename + system prompt of another
# tool already called "llm-cmd". I went looking for a good prompt
# and found one exactly like what I was about to do. So let's
# build on it.

SPROMPT = """You are a world class language translator.

Translate the provided text into English. Translate the entire provided text.

- Provide the complete translation of the text.
- Provide the language of the original text.
- Provide a simple pronunciation of the translated text for native English speakers.
- Provide any notes that might help give context for the translation.
- Break down each part of the text and provide a translation for each part.
- Do not invent or guess at a word's meaning. If you are unsure of a word's meaning, you may provide a literal translation of the word.
- Keep responses concise and to the point.
- Provide notes that might help give context for the translation.
{}

You may leave any of these blank if they are not applicable or helpful.

If you cannot confidently and correctly translate the text, leave everything else blank, but only provide an error message, such as "I cannot confidently translate this text."
"""

PROMPT_BREAKDOWN = (
    "- Break down each part of the text and provide a translation for each part."
)

# MODEL="llama3.1"
# MODEL = "mistral-small:latest"
MODEL = "deepseek-r1:14b"
# MODEL = "llama3.2"
OPTIONS = ""
TEMPERATURE = 0.15
NUM_CTX = 2048


class BreakdownPart(BaseModel):
    part: str
    translation: str


class Translation(BaseModel):
    english_translation: str
    language: str
    notes: str
    breakdown: Optional[list[BreakdownPart]]
    error_message: Optional[str]


parser = argparse.ArgumentParser(description="Translate text into English.")
# parser.add_argument(
#     "--breakdown", help="Break down each word in the translation.", action="store_true"
# )
parser.add_argument("text", nargs="*", help="The text to translate.", type=str)
args = parser.parse_args()

args.breakdown = True  # HACK


sprompt = SPROMPT.format(PROMPT_BREAKDOWN if args.breakdown else "")
response = None
try:
    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": sprompt,
            },
            {"role": "user", "content": " ".join(args.text)},
        ],
        options={"temperature": TEMPERATURE, "num_ctx": NUM_CTX},
        format=Translation.model_json_schema(),
    )

    response = response.get("message").get("content")

    # sanitize
    response = response.replace("”", '"')
    response = response.replace("“", '"')
    response = response.replace("’", "'")
    response = response.replace("‘", "'")

    response = json.loads(response)

    table = Table(show_header=False, padding=(0, 1), show_lines=False, show_edge=False)

    if "english_translation" in response and response["english_translation"] != "":
        table.add_row(
            "Translation", f"[yellow]{response['english_translation']}[/yellow]"
        )
        table.add_section()

    if "language" in response and response["language"] != "":
        table.add_row("Language", f"[cyan]{response['language']}[/cyan]")
        table.add_section()

    if "breakdown" in response and response["breakdown"] != "":
        subtable = Table(
            show_header=False, show_lines=False, padding=(0, 1), show_edge=False
        )
        subtable.add_column("Part", style="cyan")
        subtable.add_column("Translation", style="yellow")
        for part in response["breakdown"]:
            subtable.add_row(part["part"], part["translation"])
        table.add_row("Breakdown", subtable)
        table.add_section()

    if "notes" in response and response["notes"] != "":
        table.add_row("Notes", f"[green]{response['notes']}[/green]")
        table.add_section()

    if "error_message" in response and response["error_message"] != "":
        table.add_row("Error", f"[red]{response['error_message']}[/red]")

    console = Console()
    console.print(table)

    if DEBUG:
        print(sprompt)
        print()
        print(console.print(response))


except Exception as e:
    print(f"ERROR: {e}\n{response if response else ''}")
