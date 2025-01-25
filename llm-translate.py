#!/usr/bin/env python3

from typing import Optional
from pydantic import BaseModel
from rich.table import Table
from rich.console import Console

from common.LLMTool import LLMTool

# This script borrows the filename + system prompt of another
# tool already called "llm-cmd". I went looking for a good prompt
# and found one exactly like what I was about to do. So let's
# build on it.


class BreakdownPart(BaseModel):
    part: str
    translation: str


class Translation(BaseModel):
    english_translation: str
    language: str
    notes: str
    error_message: Optional[str]


class Translation_WithBreakdown(Translation):
    breakdown: list[BreakdownPart]


# -------------------------------------------------

SPROMPT = """You are a world class professional language translator. Translate the text provided by the user into English. Translate the entire provided text.

{}

- Provide the complete translation of the text.
- Provide the language of the original text.
- Provide a simple pronunciation of the translated text for native English speakers.
- Provide any notes that might help give context for the translation.
- Break down each part of the text and provide a translation for each part.
- Do not invent or guess at a word's meaning. If you are unsure of a word's meaning, you may provide a literal translation of the word.
- Do not process words that do not exist in the original text.
- Keep responses concise and to the point.
- Provide notes that might help give context for the translation.

{}

You may leave any of these blank if they are not applicable or helpful.

If you cannot confidently and correctly translate the text, leave everything else blank, but only provide an error message, such as "I cannot confidently translate this text."
"""

PROMPT_BREAKDOWN = "- Break down each part of the source text and provide a translation for each part to help the user understand how the sentence was constructed. Only break down text that is present in the original text."

# MODEL="llama3.1"
MODEL = "mistral-small:latest"
# MODEL = "deepseek-r1:14b"
# MODEL = "deepseek-r1:32b"
# MODEL = "llama3.2"
TEMPERATURE = 0.15
NUM_CTX = 2048

# -------------------------------------------------


class Translator(LLMTool):
    def setup_arguments(self, provide_text=True):
        self.arg_parser.add_argument(
            "--breakdown",
            "-b",
            help="Break down each word in the translation.",
            action="store_true",
        )
        self.arg_parser.add_argument(
            "--lang",
            help="Source language (defaults to auto-detecting).",
            type=str,
            nargs="?",
        )

        return super().setup_arguments(provide_text)

    def run(self) -> dict:
        if self.args.breakdown:
            self.response_schema = Translation_WithBreakdown.model_json_schema()
        else:
            self.response_schema = Translation.model_json_schema()

        self.sprompt = SPROMPT.format(
            PROMPT_BREAKDOWN if self.args.breakdown else "",
            "Source language is " + self.args.lang if self.args.lang else "",
        )

        return super().run()


# -------------------------------------------------

llm_tool = Translator(
    "Translate text into English.", MODEL, TEMPERATURE, NUM_CTX, Translation
)

response = llm_tool.run()

table = Table(show_header=False, padding=(0, 1), show_lines=False, show_edge=False)

if "english_translation" in response and response["english_translation"] != "":
    table.add_row("Translation", f"[yellow]{response['english_translation']}[/yellow]")
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
