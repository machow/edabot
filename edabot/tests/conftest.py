from __future__ import annotations
import pytest
from typing import TYPE_CHECKING, Iterator

from .helpers import create_shell

if TYPE_CHECKING:
    from IPython.core.interactiveshell import InteractiveShell


@pytest.fixture
def shell() -> "InteractiveShell":
    return create_shell()


@pytest.fixture
def gshell() -> Iterator[InteractiveShell]:
    """Fixture that creates a new IPython shell instance for each test."""

    from IPython.core.interactiveshell import InteractiveShell

    InteractiveShell.clear_instance()
    yield InteractiveShell.instance()
    InteractiveShell.clear_instance()
