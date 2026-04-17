from __future__ import annotations

from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt
from doctrine.parser import parse_file, parse_text

from doctrine._diagnostic_smoke.fixtures import SmokeFailure, _expect, _write_prompt


def run_parse_checks() -> None:
    _check_transform_errors_surface_as_parse_errors()
    _check_invalid_string_literals_surface_as_parse_errors()
    _check_unterminated_multiline_string_surfaces_as_parse_error()
    _check_parse_text_preserves_source_path_for_compilation()


def _check_transform_errors_surface_as_parse_errors() -> None:
    source = """workflow Shared: "Shared"
    "hi"

agent Demo:
    role: "hi"
    override workflow: Shared
        "body"
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E105", f"expected E105, got {getattr(exc, 'code', None)}")
            rendered = str(exc)
            _expect("Invalid authored slot body" in rendered, rendered)
            _expect("override workflow" in rendered, rendered)
            return
        raise SmokeFailure("expected transformer-stage parse failure, but parsing succeeded")


def _check_invalid_string_literals_surface_as_parse_errors() -> None:
    source = """agent Demo:
    role: "bad \\x"
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E106", f"expected E106, got {getattr(exc, 'code', None)}")
            rendered = str(exc)
            _expect("Invalid string literal" in rendered, rendered)
            _expect("truncated \\xXX escape" in rendered, rendered)
            return
        raise SmokeFailure("expected invalid string literal parse failure, but parsing succeeded")


def _check_unterminated_multiline_string_surfaces_as_parse_error() -> None:
    # `\"""` escapes a triple-quote sequence inside the body, but an unclosed
    # literal must still fail loudly.
    source = '''document EscapeDemo: "Escape Demo"
    markdown snippet: "Snippet" advisory
        text: """
Python code:

\\"\\"\\"
Hello, world.
'''
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            return
        raise SmokeFailure("expected unterminated multiline string parse failure, but parsing succeeded")


def _check_parse_text_preserves_source_path_for_compilation() -> None:
    source = """agent GreetingDemo:
    role: "Say hello."
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        parsed = parse_text(prompt_path.read_text(), source_path=prompt_path)
        _expect(parsed.source_path == prompt_path.resolve(), f"expected source_path {prompt_path.resolve()}, got {parsed.source_path!r}")
        rendered = compile_prompt(parsed, "GreetingDemo")
        _expect(rendered.name == "GreetingDemo", f"expected GreetingDemo, got {rendered.name}")
