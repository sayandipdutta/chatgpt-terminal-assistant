from argparse import ArgumentParser
import os
import time
from typing import Literal, TypedDict

import openai

from rich import print
from rich.panel import Panel


parser = ArgumentParser()
parser.add_argument("-h", "history", default=1, type=int)

args = parser.parse_args()
HISTORY = args.history

MODEL: Literal["gpt-3.5-turbo"] = "gpt-3.5-turbo"
MAX_HISTORY_LEN: Literal[5] = 5
MAX_RETRY: Literal[5] = 5

assert (
    0 < HISTORY < MAX_HISTORY_LEN
), f"history must be a number between 1 and {MAX_HISTORY_LEN}"

openai.api_key = os.getenv("OPENAI_API_KEY")

# TODO: tokenize messages using tiktoken to calculate no of tokens.


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class Assistant:
    conversation: list[Message] = []

    @classmethod
    def new_session(cls):
        cls.conversation = [
            {"role": "system", "content": "You are a helpful but curt assistant."},
        ]

    @classmethod
    def new_question(cls, question: str):
        message: Message = {"role": "user", "content": question}
        cls.conversation.append(message)
        response = cls.handle_response(cls.conversation)
        if not response:
            answer = "[red]No response received!!"
            print(Panel(answer, title="Assistant", subtitle=f"0 tokens consumed"))
            quit()
        reply, answer, tk = cls.process_response(response)
        cls.conversation.append(reply)
        print(Panel(answer, title="Assistant", subtitle=f"{tk} tokens consumed"))

    @staticmethod
    def handle_response(history: list[Message], retry: int = 0):
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
            if retry < 5:
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
        return response

    @staticmethod
    def process_response(response) -> tuple[Message, str, int]:
        color = "[red]"
        reply: Message = {
            "role": "assistant",
            "content": "Sorry! Could not process response!!",
        }
        total_tokens = response.usage.total_tokens

        if response.choices[0].finish_reason == "stop":
            color = "[green]"
            reply = response.choices[0].message

        answer = color + reply["content"]

        return reply, answer, total_tokens


Assistant.new_session()

for i, user_input in enumerate(iter(lambda: input("> "), "")):
    Assistant.new_question(user_input)
    if i >= HISTORY:
        print("Conversation limit reached. Please start a new session.")
        break
