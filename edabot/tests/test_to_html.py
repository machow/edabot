from edabot import to_html, execute_code

def test_to_html_execute_code(gshell, snapshot):
    res = execute_code("print('hey')\n1", as_tool=False)
    html = to_html(res)
    assert snapshot == html
