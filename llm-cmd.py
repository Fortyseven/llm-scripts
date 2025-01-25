#!/usr/bin/env python3

from typing import Optional
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
class Arguments(BaseModel):
    arg: str
    description: str


class CmdResponse(BaseModel):
    command: str
    arg_explanation: list[Arguments]
    # command_explanation: str
    notes: str
    example_usage: str
    error_message: Optional[str]
    user_request: str


# ---------------------------------------------

SPROMPT = """You are a world-class Linux administrator. You will be asked to provide a command that will run in a Ubuntu Linux desktop terminal.

- Provide the complete command that performs the operation the user wants to complete.

- Provide an explanation for what each argument does.

- Provide any notes that might help give context for the command.

- Provide your interpretation of what the user request is asking to do.

Keep responses concise and to the point.

Do not invent commands or arguments. Use only those that you are certain are available in the Ubuntu Linux desktop terminal.

If you cannot complete the request (because the user requrested an impossible thing, or provided nonsense), leave everything else blank, but only provide an error message.
"""

# MODEL = "llama3.1"
# MODEL = "llama3.2"
MODEL = "mistral-small:latest"
TEMPERATURE = 0.15
NUM_CTX = 2048


llm_tool = LLMTool(
    description="Translate a command into a Linux command.",
    model=MODEL,
    temperature=TEMPERATURE,
    num_ctx=NUM_CTX,
    response_schema=CmdResponse,
    uses_text_args=True,
)

response = llm_tool.run()

table = Table(show_header=False, padding=(0, 1), show_lines=False, show_edge=False)

# table.add_column("Command", style="cyan")

if "command" in response and response["command"] != "":
    table.add_row("Command", f"[yellow]{response['command']}[/yellow]")
    table.add_section()

# iterate each argument in the arg_explanation array
if "arg_explanation" in response and len(response["arg_explanation"]):
    subtable = Table(
        show_header=False, show_lines=False, padding=(0, 1), show_edge=False
    )
    subtable.add_column("Argument", style="cyan bold")
    subtable.add_column("Description", style="cyan")

    for explainer in response["arg_explanation"]:
        if "arg" in explainer and "description" in explainer:
            subtable.add_section()
            subtable.add_row(explainer["arg"], explainer["description"])

    table.add_row("Arguments", subtable)

    table.add_section()

if "user_request" in response and response["user_request"] != "":
    table.add_row("User Request", f"[blue]{response['user_request']}[/blue]")
    table.add_section()

if "notes" in response and response["notes"] != "":
    table.add_row("Notes", f"[purple]{response['notes']}[/purple]")
    table.add_section()

if "example_usage" in response and response["example_usage"] != "":
    table.add_row("Example Usage", f"[green]{response['example_usage']}[/green]")

if "error_message" in response and response["error_message"] != "":
    table.add_row("Error", f"[red]{response['error_message']}[/red]")

console = Console()
console.print(table)
