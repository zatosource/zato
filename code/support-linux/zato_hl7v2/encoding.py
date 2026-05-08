from __future__ import annotations


def encode_er7(value:'str', delimiters:'tuple[str, str, str, str, str]') -> 'str':
    """ Escapes HL7 delimiter characters and CR inside a field value.
    The escape character itself must be replaced first so that delimiters
    replaced later do not get double-escaped.
    """
    field, component, repetition, escape, subcomponent = delimiters

    # .. escape the escape character first to avoid double-escaping ..
    result = value
    result = result.replace(escape, f"{escape}E{escape}")

    # .. escape each delimiter with its HL7 mnemonic ..
    result = result.replace(field, f"{escape}F{escape}")
    result = result.replace(component, f"{escape}S{escape}")
    result = result.replace(repetition, f"{escape}R{escape}")
    result = result.replace(subcomponent, f"{escape}T{escape}")

    # .. CR is the HL7 segment terminator, so it must be hex-escaped
    # .. when it appears inside a field value ..
    result = result.replace('\r', f"{escape}X0D{escape}")

    return result


def decode_er7(value:'str', delimiters:'tuple[str, str, str, str, str]') -> 'str':
    """ Reverses HL7 escape sequences back to literal characters.
    The escape character itself must be restored last so that intermediate
    results do not interfere with other replacements.
    """
    field, component, repetition, escape, subcomponent = delimiters
    result = value

    # .. restore each delimiter mnemonic to its literal character ..
    result = result.replace(f"{escape}F{escape}", field)
    result = result.replace(f"{escape}S{escape}", component)
    result = result.replace(f"{escape}R{escape}", repetition)
    result = result.replace(f"{escape}T{escape}", subcomponent)

    # .. restore the hex-escaped CR back to a literal carriage return ..
    result = result.replace(f"{escape}X0D{escape}", '\r')

    # .. restore the escape character last to avoid collisions ..
    result = result.replace(f"{escape}E{escape}", escape)

    return result
