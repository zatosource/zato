from __future__ import annotations


def encode_er7(value: str, delimiters: tuple[str, str, str, str, str]) -> str:
    field, component, repetition, escape, subcomponent = delimiters
    result = value
    result = result.replace(escape, f"{escape}E{escape}")
    result = result.replace(field, f"{escape}F{escape}")
    result = result.replace(component, f"{escape}S{escape}")
    result = result.replace(repetition, f"{escape}R{escape}")
    result = result.replace(subcomponent, f"{escape}T{escape}")
    return result


def decode_er7(value: str, delimiters: tuple[str, str, str, str, str]) -> str:
    field, component, repetition, escape, subcomponent = delimiters
    result = value
    result = result.replace(f"{escape}F{escape}", field)
    result = result.replace(f"{escape}S{escape}", component)
    result = result.replace(f"{escape}R{escape}", repetition)
    result = result.replace(f"{escape}T{escape}", subcomponent)
    result = result.replace(f"{escape}E{escape}", escape)
    return result
