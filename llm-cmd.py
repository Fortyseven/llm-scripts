#!/usr/bin/env python3


# This script borrows the filename + system prompt of another
# tool already called "llm-cmd". I went looking for a good prompt
# and found one exactly like what I was about to do. So let's
# build on it.

DEBUG=False

SPROMPT="""
You are a world-class Linux administrator. You will be asked to provide a command that will run in a Ubuntu Linux desktop terminal. Provide the complete command, then an explanation for what each argument does, and any notes that might help give context for the command. Keep responses concise and to the point.

Do not invent commands or arguments. Use only those that you are certain are available in the Ubuntu Linux desktop terminal.

If you cannot complete the request, leave everything else blank, but only provide an error message.
"""

# MODEL="llama3.1"
# MODEL="mistral-small:latest"
MODEL="llama3.2"
OPTIONS=""

import sys
import json
from typing import Optional
import ollama
from rich import print
from pydantic import BaseModel
from rich.table import Table
from rich.console import Console

class Arguments(BaseModel):
    arg:str
    description:str

class CmdResponse(BaseModel):
    command: str
    arg_explanation: list[Arguments]
    # command_explanation: str
    notes: str
    example_usage: str
    error_message: Optional[str]

args = " ".join(sys.argv[1:])

if len(args) == 0:
    print("Usage: translate.py <text>")
    sys.exit(1)

response = ollama.chat(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content":SPROMPT
        },
        {
            "role": "user",
            "content": args
        }
    ],
    options={
        'temperature': 0.2,
        'num_ctx': 2048
    },
    format=CmdResponse.model_json_schema()
)

try:
    response = response.get('message').get('content')

    # sanitize
    response = response.replace("”", "\"")
    response = response.replace("“", "\"")
    response = response.replace("’", "'")
    response = response.replace("‘", "'")

    response = json.loads(response)

    table = Table(show_header=False, padding=(0, 0), show_lines=False)

    # table.add_column("Command", style="cyan")


    if 'command' in response and response['command'] != "":
        table.add_row("Command", f"[yellow]{response['command']}[/yellow]")
        table.add_section()

    # iterate each argument in the arg_explanation array
    if 'arg_explanation' in response and len(response['arg_explanation']):
        subtable = Table(show_header=False)
        subtable.add_column("Argument", style="cyan")
        subtable.add_column("Description", style="cyan")
        for explainer in response['arg_explanation']:
            if 'arg' in explainer and 'description' in explainer:
                subtable.add_row(explainer['arg'], explainer['description'])
        table.add_row("Arguments", subtable)

        table.add_section()



    if 'notes' in response and response['notes'] != "":
        table.add_row("Notes", f"[purple]{response['notes']}[/purple]")
        table.add_section()

    if 'example_usage' in response and response['example_usage'] != "":
        table.add_row("Example Usage", f"[green]{response['example_usage']}[/green]")

    if 'error_message' in response and response['error_message'] != "":
        table.add_row("Error", f"[red]{response['error_message']}[/red]")

    console = Console()
    console.print(table)

    if DEBUG:
        print(console.print(response))

except Exception as e:
    print(f"ERROR: {e}\n\n{response}")
