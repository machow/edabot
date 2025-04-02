from .chat import create_chat, create_edabot
from .execute import execute_code

def load_ipython_extension(ipython):
    from .magic import ChatMagics
    ipython.register_magics(ChatMagics)