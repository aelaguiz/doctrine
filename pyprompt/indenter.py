"""Indentation handling for the PyPrompt bootstrap grammar."""

from lark.indenter import Indenter


class PyPromptIndenter(Indenter):
    """Minimal stock-Lark indenter for the bootstrap grammar."""

    NL_type = "_NL"
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 8
