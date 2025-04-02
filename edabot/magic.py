from IPython.core.magic import Magics, magics_class, line_cell_magic
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
from IPython.core.interactiveshell import InteractiveShell


@magics_class
class ChatMagics(Magics):
    shell: InteractiveShell

    @magic_arguments()
    @argument("-c", "--chat", help="Chat variable name", default="chat")
    @argument("prompt", help="Prompt to send to the chat", nargs="*")
    @line_cell_magic
    def chat(self, line, cell=None):
        "Magic that works both as %lcmagic and as %%lcmagic"
        args = parse_argstring(self.chat, line)

        chat = self.shell.user_ns.get(args.chat, None)

        if chat is None:
            raise ValueError(f"Chat variable '{args.chat}' not found in user namespace.")

        if cell is None:
            print(line)
            chat.chat(" ".join(args.prompt))
        else:
            print(line)
            print(cell)
            chat.chat(cell)

