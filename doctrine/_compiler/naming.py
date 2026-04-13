from __future__ import annotations

import re

from doctrine._model.agent import (
    AnalysisField,
    DecisionField,
    Field,
    FinalOutputField,
    InputsField,
    OutputsField,
    ReviewField,
    SkillsField,
)
from doctrine._model.core import AddressableRef, NameRef
from doctrine._model.law import LawPath
from doctrine._compiler.constants import (
    _LAW_BEARING_AUTHORED_SLOT_KEYS,
    _ROUTE_BEARING_AUTHORED_SLOT_KEYS,
)

# Canonical naming and small address helpers previously mixed into shared.py.

_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")


def _dotted_ref_name(ref: NameRef) -> str:
    return ".".join((*ref.module_parts, ref.declaration_name))


def _agent_typed_field_key(field: Field) -> str:
    if isinstance(field, InputsField):
        return "inputs"
    if isinstance(field, OutputsField):
        return "outputs"
    if isinstance(field, AnalysisField):
        return "analysis"
    if isinstance(field, DecisionField):
        return f"decision:{_dotted_ref_name(field.value)}"
    if isinstance(field, SkillsField):
        return "skills"
    if isinstance(field, ReviewField):
        return "review"
    if isinstance(field, FinalOutputField):
        return "final_output"
    return type(field).__name__


def _authored_slot_allows_law(key: str) -> bool:
    return key in _LAW_BEARING_AUTHORED_SLOT_KEYS


def _authored_slot_carries_route_semantics(key: str) -> bool:
    return key in _ROUTE_BEARING_AUTHORED_SLOT_KEYS


def _name_ref_from_dotted_name(dotted_name: str) -> NameRef:
    parts = tuple(dotted_name.split("."))
    return NameRef(module_parts=parts[:-1], declaration_name=parts[-1])


def _law_path_from_name_ref(ref: NameRef) -> LawPath:
    return LawPath(parts=(*ref.module_parts, ref.declaration_name))


def _humanize_key(value: str) -> str:
    value = value.replace("_", " ")
    value = _CAMEL_BOUNDARY_RE.sub(" ", value)
    words = value.split()
    return " ".join(word if word.isupper() else word.capitalize() for word in words)


def _lowercase_initial(value: str) -> str:
    if not value:
        return value
    return value[0].lower() + value[1:]


def _display_addressable_ref(ref: AddressableRef) -> str:
    root = _dotted_ref_name(ref.root)
    if not ref.path:
        return root
    return f"{root}:{'.'.join(ref.path)}"
