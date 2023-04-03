import os
import time

from argparse import ArgumentParser
from datetime import datetime
from typing import Literal, TypedDict

import openai
from rich import print
from rich.console import Console

console = Console()

from formatter import format_content, welcome
from usage_tracker import record_usage

parser = ArgumentParser()
parser.add_argument("-n", "--nhistory", default=1, type=int)

args = parser.parse_args()
history = args.nhistory

MODEL: Literal["gpt-3.5-turbo"] = "gpt-3.5-turbo"
MAX_HISTORY_LEN: Literal[5] = 5
MAX_RETRY: Literal[3] = 3

THEME: Literal["gruvbox-light"] = "gruvbox-light"

assert (
    0 < history < MAX_HISTORY_LEN
), f"history must be a number between 1 and {MAX_HISTORY_LEN}"

openai.api_key = os.getenv("OPENAI_API_KEY")


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class Assistant:
    conversation: list[Message] = []
    tokens_consumed: int = 0

    @classmethod
    def new_session(cls):
        cls.conversation = [
            {"role": "system", "content": "You are a helpful but curt assistant."},
        ]
        cls.tokens_consumed = 0

    @classmethod
    def new_question(cls, question: str) -> bool:
        message: Message = {"role": "user", "content": question}
        cls.conversation.append(message)
        response = cls.handle_response(cls.conversation)
        tk = 0
        if not response:
            answer = "[red]No response received!!"
            print(format_content(answer, tokens=tk, theme=THEME))
            return False
        reply, answer, tk = cls.parse_response(response)
        cls.conversation.append(reply)
        print(format_content(answer, tokens=tk, theme=THEME))
        return True

    @classmethod
    def handle_response(cls, history: list[Message], retry: int = 0):
        # FIX: Add logging
        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=history,
            )
        except (
            openai.error.Timeout,  # type: ignore
            openai.error.APIError,  # type: ignore
            openai.error.RateLimitError,  # type:ignore
        ) as e:
            # Handle rate limit error, e.g. wait or log
            print(f"Error: {e}")
            if retry < MAX_RETRY:
                print(f"Retrying after 5 seconds.")
                time.sleep(5)
                retry += 1
                Assistant.handle_response(history, retry)
            return {}
        except (
            openai.error.PermissionError,  # type: ignore
            openai.error.AuthenticationError,  # type: ignore
            openai.error.APIConnectionError,  # type: ignore
            openai.error.InvalidRequestError,  # type: ignore
        ) as e:
            # Handle connection error, e.g. check network or log
            print(f"OpenAI error: {e}")
            return {}
        else:
            if usage := getattr(response, "usage"):
                if tokens := getattr(usage, "total_tokens"):
                    cls.tokens_consumed += tokens
        # finally:
        #     log
        return response

    @staticmethod
    def parse_response(response) -> tuple[Message, str, int]:
        reply: Message = {
            "role": "assistant",
            "content": "Sorry! Could not process response!!",
        }
        total_tokens = response.usage.total_tokens

        if response.choices[0].finish_reason == "stop":
            reply = response.choices[0].message

        answer = reply["content"]

        return reply, answer, total_tokens


welcome()
Assistant.new_session()

for i, user_input in enumerate(iter(lambda: console.input("[bold red] > "), ""), start=1):
    success = Assistant.new_question(user_input)
    if not success:
        break
    if i >= history:
        print("Conversation limit reached. Please start a new session.")
        break

record_usage(Assistant.tokens_consumed, datetime.now())
