#!/usr/bin/bash

# usage example: ol-code-breakdown.sh < source_code.py

MODEL="llama3.2:latest"

PROMPT="Analyze this source code and give a summary of it's functionality, and break down the code section by section with comments."

# set INPUT to contents of stdin

INPUT=$(cat)

ollama run $MODEL "$PROMPT: $INPUT" | pandoc -t plain
