from functools import singledispatch
from .execute import CellRun

@singledispatch
def to_html(obj) -> str:
    """Convert an object to HTML."""
    raise NotImplementedError(f"Cannot convert {type(obj)} to HTML.")

@to_html.register
def _(obj: CellRun) -> str:
    style = r"""
details.edabot-cell-run {
  /*background-color: #fbebfc;*/
  border: 2px solid #fbebfc;
  border-radius: 2px;
  & summary {
    cursor: pointer;
    padding: 10px;
    background-color: #fbebfc;
  }
}

.edabot-cell-run {
  pre {
    background-color: #f9f9f9;
    padding: 5px;
    max-height: 300px;
    overflow: scroll;
  }

  & .edabot-cell-run__section {
    padding: 5px;
  }
}
"""
    tmpl = """
<style>
{style}
</style>
<details class="edabot-cell-run">
    <summary>Execute Code</summary>
    <div class="edabot-cell-run__code edabot-cell-run__section">
      <h3>Code</h3>
      <pre>{code}</pre>
    </div>
    <div class="edabot-cell-run__outputs edabot-cell-run__section">
      <h3>Outputs</h3>
      <pre>{outputs}</pre>
    </div>
    <div class="edabot-cell-run__display edabot-cell-run__section">
      <h3>Display</h3>
      <div class="display-results">{results}</div>
    </div>
</details>
    """
    display = "\n\n".join(map(obj.output_to_html, obj.captured.outputs))

    outputs = obj.captured.stdout + "\n\n" + obj.captured.stderr

    return tmpl.format(
        style=style, outputs=outputs, results=display, code=obj.result.info.raw_cell
    )
