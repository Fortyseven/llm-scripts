#!/usr/bin/bash

MODEL="llama3.2-vision:latest"
PROMPT="Create a unique, descriptive lowercase filename for this image; return only the filename text, without commentary"

# put arguments into IMAGE_PATH

IMAGE_PATH="$1"

if [ -z "$IMAGE_PATH" ]; then
    echo "No path provided"
    exit 1
fi

# check if image exists

if [ ! -f $IMAGE_PATH ]; then
    echo "Path not found"
    exit 1
fi

EXTENSION=$(echo $IMAGE_PATH | rev | cut -d '.' -f 1 | rev)

# get IMAGE_PATH path

IMAGE_DIR=$(dirname "$IMAGE_PATH")

OUTPUT=$(llm -m "$MODEL" -a "$IMAGE_PATH" "$PROMPT")

# split by final period, save first part to BASENAME

BASENAME=$(echo $OUTPUT | cut -d '.' -f 1)

# strip spaces from BASENAME

BASENAME=$(echo $BASENAME | tr -d ' ')

# ask user if new filename is acceptable

echo "New filename: $BASENAME.$EXTENSION"
read -p "Accept? (y/n) " -n 1 -r

if [[ $REPLY =~ ^[Yy]$ ]]; then
    mv "$IMAGE_PATH" "$IMAGE_DIR/$BASENAME.$EXTENSION"
    echo "OK"
else
    echo "Aborted"
fi
