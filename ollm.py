#!/usr/bin/env python3

"""
This is a flimsy Ollama-specific implementation of Datasette's "LLM" tool. Right up until I found out there was already Ollama compatibility available if I'd just dig a bit further. Oh well.

This script is largely abandoned, and is probably incomplete. It's here for posterity. Or maybe it'll help someone else.

https://llm.datasette.io/
"""

# ./ollm.py -i ollm.py "Write a joke about this code." | /home/fortyseven/opt/ai/piper/piper --model /home/fortyseven/opt/ai/glados/models/glados.onnx --output-raw | aplay -r 22050 -f S16_LE -t raw -

import ollama
import argparse

DEFAULT_MODEL = "llama3.1:latest"
DEFAULT_CONTEXT_SIZE = 64 * 1024  # 64KB

parser = argparse.ArgumentParser(description="ollm: One Line Language Model")
parser.add_argument("input", type=str, nargs="?", help="input text")
parser.add_argument(
    "-i", "--input-file", type=str, help="input file to read from", default=None
)
parser.add_argument(
    "-m", "--model", type=str, help="model name to use", default=DEFAULT_MODEL
)
parser.add_argument("-o", "--output", type=str, help="output file")
parser.add_argument("-t", "--temperature", type=float, help="temperature", default=0.75)
parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
# parser.add_argument("-p", "--payload", type=str, help="payload", default=None)
args = parser.parse_args()


if not args.input and not args.input_file:
    parser.error('Either quoted "input"  text or --input-file must be specified.')

# read input
input_prompt = ""

if args.input:
    input_prompt = args.input

if len(input_prompt) and args.input_file:
    payload = open(args.input_file, "r").read()
    input_prompt = f"{input_prompt}\n####\n{payload}"
elif args.input_file:
    with open(args.input_file, "r") as f:
        input_prompt = f.read()


# read model
model_name = args.model

# if args.verbose:
#     print(f"Model: {model_name}")
#     print(f"Input: {input_prompt}")


# run ollm
output_text = ollama.generate(
    model=model_name,
    prompt=input_prompt,
    options={"temperature": args.temperature, "num_ctx": DEFAULT_CONTEXT_SIZE},
)["response"]

# write output

if args.output:
    with open(args.output, "w") as f:
        f.write(output_text)
elif not args.verbose:
    print(output_text)

# if args.verbose:
#     print(f"\n\nOutput: {output_text}")
