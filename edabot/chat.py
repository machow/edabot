from __future__ import annotations

import pystache
import os
from chatlas import ChatAnthropic
from ._chatlas import Chat2
from dotenv import find_dotenv, dotenv_values
from importlib.resources import files
from .execute import execute_code, create_quarto_report
from pathlib import Path


def create_edabot(system_prompt: str | None = None) -> Chat2:
    chat = create_chat(system_prompt)
    chat.register_tool(execute_code)
    chat.register_tool(create_quarto_report)
    return chat


def create_chat(system_prompt: str | None = None) -> Chat2:
    env = dotenv_values(find_dotenv())
    api_key = env.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY"))
    if api_key is None:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in environment variables or .env file."
        )
    
    if system_prompt is None:
        prompt = files("edabot").joinpath("prompts/01-databot.md").read_text()

        p_llms = Path("./llms.txt")
        system_prompt = pystache.render(prompt, {
            "has_llms_txt": p_llms.exists(),
            "llms_txt": p_llms.read_text() if p_llms.exists() else "",
        })


    chat = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        system_prompt=system_prompt,
        api_key=api_key,
    )

    chat.__class__ = Chat2
    return chat
