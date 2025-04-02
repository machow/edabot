from ._chatlas import ctx_display
from .chat import create_chat, create_edabot
from .execute import execute_code
from .to_html import to_html

def load_ipython_extension(ipython):
    from .magic import ChatMagics
    ipython.register_magics(ChatMagics)