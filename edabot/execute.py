from __future__ import annotations

import traceback
from chatlas.types import (
    Content,
    ContentImageInline,
    ContentText,
    ContentToolResult,
    ContentJson,
)
from dataclasses import dataclass
from typing import Any, Union, TYPE_CHECKING, Literal, overload
from typing_extensions import TypeAlias

from ._chatlas import ctx_display

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell, ExecutionResult
    from IPython.utils.capture import RichOutput, CapturedIO

CellException: TypeAlias = "tuple[type, BaseException, Any]"


@dataclass
class CellRun:
    """The result of executing an IPython cell.

    Attributes
    ----------
    captured:
        The captured stdout, stderr, and rich outputs.
    result:
        The returned value of the cell (resulting from the last expression).
    execution_info:
        Information about execution.
    """

    captured: CapturedIO
    result: ExecutionResult
    execution_info: Union[CellException, None]

    def to_content(self) -> list[Content]:
        return list(map(self.output_to_content, self.captured.outputs))

    def to_tool_result(self) -> ContentToolResult:
        if self.execution_info is not None:
            tb = traceback.format_exception(*self.execution_info)
        else:
            tb = []
        cell_std = ContentJson(
            {
                "type": "stdout, stderr, and exceptions",
                "stdout": self.captured.stdout,
                "stderr": self.captured.stderr,
                "raw_cell": self.result.info.raw_cell,
                # TODO: might want traceback
                "error": bool(tb),
                "error_traceback": tb,
            }
        )
        cell_displays = self.to_content()
        return ContentToolResult("", [cell_std, *cell_displays])

    @staticmethod
    def output_to_html(output: "RichOutput | str") -> str:
        if isinstance(output, str):
            return output

        if (res := output._repr_mime_("image/png")) is not None:
            return f'<img src="data:image/png;base64,{res[0]}" />'
        elif (res := output._repr_mime_("text/html")) is not None:
            return res[0]

        return output.data.get("text/plain", "")

    @staticmethod
    def output_to_content(output: RichOutput) -> Content:
        if (res := output._repr_mime_("image/png")) is not None:
            # res is data and metadata
            return ContentImageInline("image/png", res[0])
        elif (res := output._repr_mime_("text/html")) is not None:
            return ContentText("text/html", res[0])

        return ContentText(output.data.get("text/plain", ""))


def run_cell_capture_exceptions(shell: InteractiveShell, code: str) -> CellRun:
    from IPython.utils.capture import capture_output

    # Create a variable to store the exception if one occurs
    exception_info = None

    # Define a custom error handler function
    def custom_handler(shell, etype, evalue, tb, tb_offset=None):
        nonlocal exception_info
        exception_info = (etype, evalue, tb)
        # return shell.InteractiveTB.handler(etype, evalue, tb, tb_offset)

    # Store the original exception handler
    original_handler = shell.custom_exceptions

    try:
        # Set our custom handler
        shell.set_custom_exc((Exception,), custom_handler)

        # Run the cell with output capture
        with capture_output() as captured:
            result = shell.run_cell(code)

        return CellRun(captured, result, exception_info)
    finally:
        # Restore the original handler
        shell.custom_exceptions = original_handler

        # TODO: handle worst case CellRun return


@overload
def execute_code(code: str, as_tool: Literal[True]) -> ContentToolResult: ...


@overload
def execute_code(code: str, as_tool: Literal[False]) -> CellRun: ...


def execute_code(code: str, as_tool: bool = True):
    """Execute python code in the current IPython shell.
    
    When running with as_tool=True, the code, along with any output displayed
    results get shown in the notebook output (similar to running the code directly
    from a jupyter notebook cell).
    """

    from IPython.core.getipython import get_ipython
    from IPython.display import display, HTML

    shell = get_ipython()

    if shell is None:
        raise ValueError("Result of get_ipython() is None.")

    cell_run = run_cell_capture_exceptions(shell, code)
    # with capture_output() as cap:
    #    res = shell.run_cell(code, store_history=False)

    if as_tool:
        from edabot.to_html import to_html
        display(HTML(to_html(cell_run)))
        displayer = ctx_display.get()
        displayer._init_display()
        return cell_run.to_tool_result()

    return cell_run


def create_quarto_report(filename: str, content: str, as_tool: bool = True) -> str:
    """Create a Quarto report from the given content."""

    # Create the Quarto report
    with open(filename, "w") as f:
        f.write(content)
    
    print("\n\nQUARTO REPORT CREATED:", filename)