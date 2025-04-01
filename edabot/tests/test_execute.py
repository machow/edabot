from edabot.execute import execute_code, run_cell_capture_exceptions


def test_run_cell(shell):
    res = run_cell_capture_exceptions(shell, "x = 1")
    assert res.result.result is None
    assert shell.run_cell("x").result == 1


def test_execute_code(gshell):
    res = execute_code("x = 1", as_tool=False)
    assert res.result.result is None
    assert gshell.run_cell("x").result == 1
