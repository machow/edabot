import os
from chatlas import Chat, ChatAnthropic
from dotenv import find_dotenv, dotenv_values

from .execute import execute_code


def create_edabot() -> Chat:
    chat = create_chat()
    chat.register_tool(execute_code)
    return chat


def create_chat() -> Chat:
    env = dotenv_values(find_dotenv())
    return ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        system_prompt="You are a friendly but terse assistant.",
        api_key=env["ANTHROPIC_API_KEY"],
    )
