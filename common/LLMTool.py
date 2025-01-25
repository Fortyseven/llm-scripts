from abc import abstractmethod
import argparse
from typing import Optional, List, Dict, Any
import json
import ollama
from pydantic import BaseModel
from rich.table import Table
from rich.console import Console


class LLMTool:
    def __init__(
        self,
        description: str,
        model: str,
        temperature: float,
        num_ctx: int,
        response_schema: object,
        uses_text_args: bool = True,
    ):
        self.debug = False
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.sprompt = ""
        self.response_schema = None
        self.arg_parser = argparse.ArgumentParser(description=description)
        self.args = None
        self.uses_text_args = False
        self.setup_arguments(uses_text_args)

    @abstractmethod
    def setup_arguments(self, provide_text: bool = True):
        self.arg_parser.add_argument(
            "--debug", help="Print debug information.", action="store_true"
        )

        self.arg_parser.add_argument(
            "--model", help="Override default model", type=str, nargs="?"
        )

        if provide_text:
            self.uses_text_args = True
            self.arg_parser.add_argument(
                "text", nargs="*", help="The text to translate.", type=str
            )

        self.args = self.arg_parser.parse_args()

        if self.args.model:
            self.model = self.args.model.strip()

        if self.uses_text_args:
            if len(self.args.text) == 0:
                self.arg_parser.print_help()
                exit(1)

    @abstractmethod
    def run(self) -> dict:

        if self.args.debug:
            self.debug = True

        # if len(args.text) == 0:
        #     self.arg_parser.print_help()
        #     sys.exit(1)

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.sprompt,
                    },
                    {"role": "user", "content": " ".join(self.args.text)},
                ],
                options={"temperature": self.temperature, "num_ctx": self.num_ctx},
                format=self.response_schema,
            )

            response = response.get("message").get("content")

            # sanitize
            response = response.replace("”", '"')
            response = response.replace("“", '"')
            response = response.replace("’", "'")
            response = response.replace("‘", "'")

            response = json.loads(response)

            return response

        except Exception as e:
            print(f"ERROR: {e}")
            return {}
