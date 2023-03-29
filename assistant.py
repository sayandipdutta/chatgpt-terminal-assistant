import os
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
        message: Message = {'role': 'user', 'content': question}
        cls.conversation.append(message)
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=cls.conversation,
        )
        reply, answer, tk = cls.process_response(response)
        cls.conversation.append(reply)
        print(Panel(answer, title="Assistant", subtitle=f"{tk} tokens consumed"))

    @staticmethod
    def process_response(response) -> tuple[Message, str, int]:
        color = '[red]'
        if response.choices[0].finish_reason == 'stop':
            color = '[green]'
            pass
        reply: Message = response.choices[0].message
        total_tokens = response.usage.total_tokens

        answer = color + reply['content']
        return reply, answer, total_tokens


for user_input in iter(lambda: input("> "), ''):
    Assistant.new_session()
    Assistant.new_question(user_input)



