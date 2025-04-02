# edabot

## Basic use

```python
# In a jupyter notebook --------

from edabot import create_edabot

# assumes ANTHROPIC_API_KEY in .env
chat = create_edabot()
chat.chat("""
    You are a data analyst working in IPython.  Any code you
    execute is run as cells in a jupyter notebook.  First, inspect
    the variables in your environment, then check the columns of
    the penguins dataframe, then generate a scatter plot using
    plotnine and the penguins data in plotnine.data (with the
    ggplot function).
""")
```

## Chat magic

```python
from edabot import create_edabot

# assumes ANTHROPIC_API_KEY in .env
chat = create_edabot()
```

Now you can use jupyter cell magics:

```python
%%chat

Print out the time.
```
