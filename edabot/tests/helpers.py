from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell


def create_shell() -> InteractiveShell:
    from IPython.core.interactiveshell import InteractiveShell

    shell = InteractiveShell()
    return shell
