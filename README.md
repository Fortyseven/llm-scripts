This is a personal collection of small LLM scripts using [Ollama](https://ollama.com/) to do various tasks on the command line. The aim is to keep these independent of each other, never exceeding one file in size.


I'm not currently accepting patches or bug fixes, but feel free to toss over suggestions for improvements, or point out other small scripts that might be of interest.

# Requirements

 Versions mentioned are NOT hard requirements, but simply what I was using at development time.

- **Ollama**
- For **Python** scripts:
    - Python 3.12 (though none use anything bleeding edge, so give it a go)
    - Most require the `ollama` and `rich` packages; but these are so common for me I just tossed them into my system Python.
- For **shell** scripts:
    - Bash on Ubuntu; nothing special
    - I'd be surprised if I was using anything beyond basic shell utilities in them, but beware.
