# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import ast
import re

# Zato
from zato.common.rules.document import Value_Type_Datetime, list_node, literal_node, object_node, reference_node

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Identifiers may be dotted paths, e.g. customer.creditScore or default.min_score.
identifier_pattern = re.compile(r'^[A-Za-z_][\w.]*$')

# Rule names may additionally start with a digit, e.g. 01_Regex_Basic_Test.
rule_name_pattern = re.compile(r'^\w+$')

# Plain integer and floating-point literals.
_integer_pattern = re.compile(r'^[+-]?\d+$')
_float_pattern   = re.compile(r'^[+-]?(\d+\.\d*|\.\d+)$')

# The two quote characters string literals may use.
_quote_characters = ('"', "'")

# Boolean keywords accepted in the text form, canonically lowercase.
_boolean_values = {
    'true':  True,
    'false': False,
    'True':  True,
    'False': False,
}

# ################################################################################################################################
# ################################################################################################################################

def strip_comment(line:'str') -> 'str':
    """ Removes a trailing # comment from a line, leaving # characters inside quoted strings intact.
    """

    # Scan the line character by character, tracking whether we are inside a quoted string ..
    quote = ''
    is_escaped = False

    for index, character in enumerate(line):

        # .. a backslash inside a string escapes whatever follows it ..
        if is_escaped:
            is_escaped = False
            continue

        if quote:
            if character == '\\':
                is_escaped = True
            elif character == quote:
                quote = ''

        # .. outside a string, a quote opens one and a hash starts the comment.
        elif character in _quote_characters:
            quote = character
        elif character == '#':
            return line[:index]

    return line

# ################################################################################################################################

def find_top_level(text:'str', wanted:'str') -> 'int':
    """ Returns the index of the first occurrence of a character outside quotes and brackets, or -1.
    """

    # Scan the text, tracking quote state and bracket depth ..
    quote = ''
    is_escaped = False
    depth = 0

    for index, character in enumerate(text):

        # .. escapes inside strings never count ..
        if is_escaped:
            is_escaped = False
            continue

        if quote:
            if character == '\\':
                is_escaped = True
            elif character == quote:
                quote = ''
            continue

        if character in _quote_characters:
            quote = character
        elif character in '[{':
            depth += 1
        elif character in ']}':
            depth -= 1

        # .. and only a top-level occurrence is a hit.
        elif character == wanted:
            if depth == 0:
                return index

    return -1

# ################################################################################################################################

def split_top_level(text:'str', separator:'str') -> 'strlist':
    """ Splits text on a separator character, ignoring separators inside quotes and brackets.
    """
    out = []
    remaining = text

    # Keep cutting off the part before each top-level separator ..
    while True:
        index = find_top_level(remaining, separator)
        if index == -1:
            break
        out.append(remaining[:index])
        remaining = remaining[index+1:]

    # .. and whatever remains is the last part.
    out.append(remaining)

    return out

# ################################################################################################################################

def has_top_level_parenthesis(text:'str') -> 'bool':
    """ Returns True if the text contains a parenthesis outside quoted strings.
    """
    opening = find_top_level(text, '(')
    closing = find_top_level(text, ')')

    out = opening != -1 or closing != -1
    return out

# ################################################################################################################################
# ################################################################################################################################

def _unescape(text:'str', quote:'str') -> 'str':
    """ Undoes backslash escapes for the quote character and the backslash itself, keeping everything else verbatim.
    """
    out = []
    is_escaped = False

    for character in text:

        # After a backslash, the quote and another backslash are taken literally ..
        if is_escaped:
            if character in (quote, '\\'):
                out.append(character)

            # .. anything else keeps both characters, e.g. regex classes like \s.
            else:
                out.append('\\')
                out.append(character)
            is_escaped = False

        elif character == '\\':
            is_escaped = True

        else:
            out.append(character)

    # A trailing lone backslash stays as it is.
    if is_escaped:
        out.append('\\')

    result = ''.join(out)
    return result

# ################################################################################################################################

def _parse_quoted(text:'str') -> 'anydict | None':
    """ Parses a quoted string literal, with an optional r prefix, returning None if the text is not one.
    """

    # An r prefix marks a regex-style raw string, the content is the same either way ..
    if text.startswith(('r"', "r'")):
        text = text[1:]

    # .. the text must start and end with the same quote character ..
    first = text[0]
    if first not in _quote_characters:
        return None

    if len(text) < 2:
        return None

    if not text.endswith(first):
        return None

    # .. and the value is the unescaped content between the quotes.
    inner = text[1:-1]
    value = _unescape(inner, first)

    out = literal_node(value)
    return out

# ################################################################################################################################

def parse_scalar(text:'str') -> 'anydict | None':
    """ Parses a single scalar value into a tagged node - literal, datetime literal or reference - or None.
    """
    text = text.strip()

    # There has to be anything to parse at all ..
    if not text:
        return None

    # .. datetime literals use their dedicated d'...' syntax ..
    if text.startswith("d'"):
        if text.endswith("'"):
            inner = text[2:-1]
            out = literal_node(inner, Value_Type_Datetime)
            return out
        else:
            return None

    # .. quoted strings become string literals ..
    if text.startswith(('"', "'", 'r"', "r'")):
        out = _parse_quoted(text)
        return out

    # .. boolean keywords become boolean literals ..
    if text in _boolean_values:
        out = literal_node(_boolean_values[text])
        return out

    # .. numbers become numeric literals ..
    if _integer_pattern.match(text):
        out = literal_node(int(text))
        return out

    if _float_pattern.match(text):
        out = literal_node(float(text))
        return out

    # .. and a bare identifier is a reference to another term.
    if identifier_pattern.match(text):
        out = reference_node(text)
        return out

    # Anything else is not a scalar we recognize.
    return None

# ################################################################################################################################

def _parse_bracket_list(text:'str') -> 'anydict | None':
    """ Parses a [...] list into a list node whose items are scalar nodes, or None on failure.
    """

    # The brackets must balance ..
    if not text.endswith(']'):
        return None

    # .. an empty list is a valid, if unusual, value ..
    inner = text[1:-1].strip()
    if not inner:
        out = list_node([])
        return out

    # .. and each comma-separated part must be a scalar.
    items = []
    for part in split_top_level(inner, ','):
        item = parse_scalar(part)
        if item is None:
            return None
        items.append(item)

    out = list_node(items)
    return out

# ################################################################################################################################

def parse_value(text:'str') -> 'anydict | None':
    """ Parses an action or default value - a scalar, a comma list, a [...] list or a {...} object - or None.
    """
    text = text.strip()

    # Objects use explicit brace syntax and must evaluate to a mapping ..
    if text.startswith('{'):
        try:
            value = ast.literal_eval(text)
        except (SyntaxError, ValueError):
            return None
        if not isinstance(value, dict):
            return None
        out = object_node(value)
        return out

    # .. bracket lists use explicit bracket syntax ..
    if text.startswith('['):
        out = _parse_bracket_list(text)
        return out

    # .. a top-level comma makes the value a list of scalars ..
    comma_index = find_top_level(text, ',')
    if comma_index != -1:
        items = []
        for part in split_top_level(text, ','):
            item = parse_scalar(part)
            if item is None:
                return None
            items.append(item)
        out = list_node(items)
        return out

    # .. and everything else is a single scalar.
    out = parse_scalar(text)
    return out

# ################################################################################################################################
# ################################################################################################################################
