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
from typing import Any, Union, TYPE_CHECKING
from typing_extensions import TypeAlias

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

    def to_html(self) -> str:
        tmpl = """
        <details>
          <summary>Execute Code</summary>
          <h3>Code</h3>
          <pre>{code}</pre>
          <h3>Outputs</h3>
          <pre>
          {outputs}
          </pre>

          <h3>Display</h3>
          {results}
        </details>
        """
        display = "\n\n".join(map(self.output_to_html, self.captured.outputs))

        outputs = self.captured.stdout + "\n\n" + self.captured.stderr

        return tmpl.format(
            outputs=outputs, results=display, code=self.result.info.raw_cell
        )

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


def execute_code(code: str, as_tool: bool = True):
    """Execute python code in the current IPython shell."""

    from IPython.core.getipython import get_ipython
    from IPython.display import display, HTML

    shell = get_ipython()

    if shell is None:
        raise ValueError("Result of get_ipython() is None.")

    cell_run = run_cell_capture_exceptions(shell, code)
    # with capture_output() as cap:
    #    res = shell.run_cell(code, store_history=False)

    if as_tool:
        display(HTML(cell_run.to_html()))
        return cell_run.to_tool_result()

    return cell_run
