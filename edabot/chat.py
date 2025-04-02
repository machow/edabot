from __future__ import annotations

import os
from chatlas import ChatAnthropic
from ._chatlas import Chat2
from dotenv import find_dotenv, dotenv_values

from .execute import execute_code


def create_edabot() -> Chat2:
    chat = create_chat()
    chat.register_tool(execute_code)
    return chat


def create_chat() -> Chat2:
    env = dotenv_values(find_dotenv())
    api_key = env.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY"))
    if api_key is None:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment variables or .env file."
        )
    chat = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        system_prompt="You are a friendly but terse assistant.",
        api_key=api_key,
    )

    chat.__class__ = Chat2
    return chat
