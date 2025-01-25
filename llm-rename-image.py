#!/usr/bin/env python3

from typing import List, Optional
from rich import print
from pydantic import BaseModel

from rich.table import Table
from rich.console import Console

from common.LLMTool import LLMTool

# This script borrows the filename + system prompt of another
# tool already called "llm-cmd". I went looking for a good prompt
# and found one exactly like what I was about to do. So let's
# build on it.


# ---------------------------------------------


class ImageNameOptions(BaseModel):
    description: str
    name_choices: List[str]


class ImageRename(LLMTool):
    def setup_arguments(self, provide_text=True, text_as_filepath=True):
        return super().setup_arguments(provide_text, text_as_filepath)


# ---------------------------------------------

MODEL = "llama3.2-vision:latest"

SPROMPT = """Visually describe this image accounting for every item in the image including text and distinct objects; read the text if it exists; then create a set of 5 unique, verbose, descriptive lowercase filenames as name_choices based on that description. Vary it up. Have some short, some verbose and descriptive."""

TEMPERATURE = 0.4

NUM_CTX = 4096


llm_tool = ImageRename(
    description="Provides a set of unique, verbose, descriptive lowercase filenames based on image content.",
    model=MODEL,
    temperature=TEMPERATURE,
    sprompt=SPROMPT,
    num_ctx=NUM_CTX,
    response_schema=ImageNameOptions,
    uses_text_args=True,
)

response = llm_tool.run()

console = Console()

console.print(
    f"[blue]What I saw:[/blue][bright_blue]{ response['description'] }[/bright_blue]"
)
console.print("")
for i, name in enumerate(response["name_choices"]):
    console.print(f"{i+1}. {name}")

# pick one

choice = input("\nPick a filename: ")

if choice.isdigit():
    choice = int(choice)
    if choice > 0 and choice <= len(response["name_choices"]):
        print(response["name_choices"][choice - 1])
    else:
        print("Invalid choice.")
