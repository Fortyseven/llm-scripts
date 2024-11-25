#!/usr/bin/bash

# usage example: llm-summarize.sh textfile.txt

MODEL="llama3.1:latest"

PROMPT="Summarize the following text as an HTML. Provide a brief summary of what the text is about, including the main points and key details. The summary should be concise and to the point. Also provide a short list of bullet points highlighting the overall key details. Use the provided example output to format the response.

IMPORTANT: Do NOT include opinion, interpretations, or infer additional context where it does not exist in the provided text. Only use the information provided in the text. Do not invent information. Strive for accuracy using ONLY the information provided. This is true for the summary, or for follow-up questions asked by the user about the text: only use what is provided in the text.
----
Example output:
# SUMMARY
Summary text.

# MAIN POINTS
- Point 1
- Point 2

# KEY DETAILS
- Detail 1
- Detail 2
"

OPTIONS="-o temperature 0.2 -o num_ctx 65535"

# check if $1 exists

if [ -z "$1" ]; then
    echo "No path provided"
    exit 1
fi

# warn if file larger than 64k and truncate

if [ $(wc -c < $1) -gt 65535 ]; then
    echo "WARNING: file is larger than 64k, which may exceed the token limit for the current context size."
    echo
fi

# ollama run $MODEL "$PROMPT $INPUT"
llm $OPTIONS --model $MODEL --system "$PROMPT" < $1
