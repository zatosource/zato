from __future__ import annotations

import re


def encode_er7(value: str, delimiters: tuple[str, str, str, str, str]) -> str:
    field, component, repetition, escape, subcomponent = delimiters
    result = value
    result = result.replace(escape, f'{escape}E{escape}')
    result = result.replace(field, f'{escape}F{escape}')
    result = result.replace(component, f'{escape}S{escape}')
    result = result.replace(repetition, f'{escape}R{escape}')
    result = result.replace(subcomponent, f'{escape}T{escape}')
    return result


def decode_er7(value: str, delimiters: tuple[str, str, str, str, str]) -> str:
    field, component, repetition, escape, subcomponent = delimiters
    result = value

    # .. Mnemonic escapes for delimiters.
    result = result.replace(f'{escape}F{escape}', field)
    result = result.replace(f'{escape}S{escape}', component)
    result = result.replace(f'{escape}R{escape}', repetition)
    result = result.replace(f'{escape}T{escape}', subcomponent)
    result = result.replace(f'{escape}E{escape}', escape)

    # .. Highlighting markers - presentation-only, strip them.
    result = result.replace(f'{escape}H{escape}', '')
    result = result.replace(f'{escape}N{escape}', '')

    # .. Character set escapes - strip the markers.
    esc_re = re.escape(escape)
    result = re.sub(f'{esc_re}C[^{esc_re}]*{esc_re}', '', result)
    result = re.sub(f'{esc_re}M[^{esc_re}]*{esc_re}', '', result)

    # .. Formatting codes.
    result = re.sub(f'{esc_re}\\.br{esc_re}', '\n', result)
    result = re.sub(f'{esc_re}\\.sp (\\d+){esc_re}', _sp_replace, result)
    result = re.sub(f'{esc_re}\\.sp{esc_re}', '\n', result)
    result = re.sub(f'{esc_re}\\.fi{esc_re}', '', result)
    result = re.sub(f'{esc_re}\\.nf{esc_re}', '', result)

    return result


def _sp_replace(match: 're.Match[str]') -> str:
    line_count = int(match.group(1))
    return '\n' * line_count
