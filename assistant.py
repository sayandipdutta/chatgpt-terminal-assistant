import os
import time
from typing import Literal, TypedDict

import openai

from rich import print
from rich.panel import Panel


MODEL: Literal["gpt-3.5-turbo"] = "gpt-3.5-turbo"
openai.api_key = os.environ["OPENAI_API_KEY"]

# TODO: tokenize messages using tiktoken to calculate no of tokens.
# print(response)


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
        except openai.error.Timeout as e:
            # Handle timeout error, e.g. retry or log
            print(f"OpenAI API request timed out: {e}")
            if retry < 5:
                print(f"Retrying after 5 seconds.")
                time.sleep(5)
                retry += 1
                Assistant.handle_response(history, retry)
            return {}
        except openai.error.APIError as e:
            # Handle API error, e.g. retry or log
            print(f"OpenAI API returned an API Error: {e}")
            if retry < 5:
                print(f"Retrying after 5 seconds.")
                time.sleep(5)
                retry += 1
                Assistant.handle_response(history, retry)
            return {}
        except openai.error.APIConnectionError as e:
            # Handle connection error, e.g. check network or log
            print(f"OpenAI API request failed to connect: {e}")
            return {}
        except openai.error.InvalidRequestError as e:
            # Handle invalid request error, e.g. validate parameters or log
            print(f"OpenAI API request was invalid: {e}")
            return {}
        except openai.error.AuthenticationError as e:
            # Handle authentication error, e.g. check credentials or log
            print(f"OpenAI API request was not authorized: {e}")
            return {}
        except openai.error.PermissionError as e:
            # Handle permission error, e.g. check scope or log
            print(f"OpenAI API request was not permitted: {e}")
            return {}
        except openai.error.RateLimitError as e:
            # Handle rate limit error, e.g. wait or log
            print(f"OpenAI API request exceeded rate limit: {e}")
            if retry < 5:
                print(f"Retrying after 5 seconds.")
                time.sleep(5)
                retry += 1
                Assistant.handle_response(history, retry)
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


for user_input in iter(lambda: input("> "), ""):
    Assistant.new_session()
    Assistant.new_question(user_input)
