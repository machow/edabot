from __future__ import annotations
import contextvars
from chatlas import Chat 
from chatlas._display import MarkdownDisplay, IPyMarkdownDisplay

ctx_display: contextvars.ContextVar[IPyMarkdownDisplay] = contextvars.ContextVar("display")


class IPyMarkdownDisplay2(IPyMarkdownDisplay):
    _token: contextvars.Token | None = None

    def _init_display(self) -> str:
        # NOTE: now reset content
        self.content = ""

        try:
            from IPython.display import HTML, Markdown, display
        except ImportError:
            raise ImportError(
                "The IPython package is required for displaying content in a Jupyter notebook. "
                "Install it with `pip install ipython`."
            )

        # NOTE: removed the displayed, malformed HTML
        if self._css_styles:
            pass

        handle = display(Markdown(""), display_id=True)
        if handle is None:
            raise ValueError("Failed to create display handle")

        # NOTE: now assign display id
        self._ipy_display_id = handle.display_id
        return handle.display_id

    def __enter__(self):
        self._token = ctx_display.set(self)
        return super().__enter__()
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self._token is not None:
            ctx_display.reset(self._token)

        
class Chat2(Chat):
    def _markdown_display(self, *args, **kwargs) -> MarkdownDisplay:
        display = super()._markdown_display(*args, **kwargs)
        if isinstance(display, IPyMarkdownDisplay):
            return IPyMarkdownDisplay2(self._echo_options)
        
        return display