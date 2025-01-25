from abc import abstractmethod
import argparse
from typing import Optional, List, Dict, Any
import json
import ollama
from pydantic import BaseModel
from rich import print
from rich.table import Table
from rich.console import Console


class LLMTool:
    def __init__(
        self,
        description: str,
        model: str,
        temperature: float,
        num_ctx: int = None,
        response_schema: object = None,
        uses_text_args: bool = True,
    ):
        """
        Initialize the LLMTool class. This class is a base class for all LLM tools. It provides a common interface for setting up arguments and running the tool.

        Args:
            description (str): Description of the tool.
            model (str): The model to use.
            temperature (float): The inference temperature.
            num_ctx (int): The number of contexts to use. Defaults to undefined.
            response_schema (object, optional):  Defaults to None.
            uses_text_args (bool, optional):  Defaults to True.
        """
        self.debug = False
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.sprompt = ""
        self.response_schema = response_schema
        self.arg_parser = argparse.ArgumentParser(description=description)
        self.seed = None
        self.args = None
        self.uses_text_args = False
        self.setup_arguments(uses_text_args)

    # to string
    def __str__(self):
        return f"""
Model: {self.model},
Temperature: {self.temperature},
NumCtx: {self.num_ctx},
Seed: {self.seed},
SPrompt: {self.sprompt},
Args: {self.args},
UsesTextArgs: {self.uses_text_args},
ResponseSchema: {self.response_schema}
"""

    @abstractmethod
    def setup_arguments(self, provide_text: bool = True):
        self.arg_parser.add_argument(
            "--debug", help="Print debug information.", action="store_true"
        )

        self.arg_parser.add_argument(
            "--model", "-m", help="Override default model", type=str, nargs="?"
        )

        self.arg_parser.add_argument(
            "--temperature",
            "-t",
            help="Override default temperature",
            type=float,
            nargs="?",
        )

        self.arg_parser.add_argument(
            "--seed",
            "-s",
            help="Force seed value",
            type=int,
            nargs="?",
        )

        if provide_text:
            self.uses_text_args = True
            self.arg_parser.add_argument(
                "text", nargs="*", help="The text to translate.", type=str
            )

        self.args = self.arg_parser.parse_args()

        if self.args.model:
            self.model = self.args.model.strip()

        if self.args.temperature:
            self.temperature = self.args.temperature

        if self.args.seed is not None:
            self.seed = self.args.seed

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
            options = {
                "temperature": self.temperature,
                "model": self.model,
            }

            if self.num_ctx:
                options["num_ctx"] = self.num_ctx

            if self.seed is not None:
                print(f"Using seed: {self.seed}")
                options["seed"] = self.seed

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.sprompt,
                    },
                    {"role": "user", "content": " ".join(self.args.text)},
                ],
                options=options,
                format=self.response_schema,
            )

            response = response.get("message").get("content")

            # sanitize
            response = response.replace("”", '"')
            response = response.replace("“", '"')
            response = response.replace("’", "'")
            response = response.replace("‘", "'")

            response = json.loads(response)

            if self.debug:
                print("\n-- LLMTOOL ----------\n")
                print(self)
                print("\n-- RESPONSE ---------\n")
                print(response)
                print("\n------------\n")

            return response

        except Exception as e:
            print(f"ERROR: {e}")
            return {}
