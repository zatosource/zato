# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Reading VS Code theme sources - JSONC files with // and /* */ comments
# and trailing commas - and following their include chains.

# stdlib
import json
import os

# Zato
from zato.common.typing_ import anydict, strlist
from zato.common.webapp.ui.themes.tokens import ThemeConversionError

# ################################################################################################################################
# ################################################################################################################################

def _strip_comments(text:'str', name:'str') -> 'str':
    """ Removes // and /* */ comments outside strings. A tiny scanner rather
    than a regex, because values like vscode://schemas contain slashes.
    """
    out:'strlist' = []
    index = 0
    length = len(text)
    in_string = False

    # Walk the text once, copying everything that is not a comment ..
    while index < length:
        char = text[index]

        if in_string:
            out.append(char)

            # .. a backslash escapes the next character, including a quote ..
            if char == '\\':
                if index + 1 < length:
                    out.append(text[index + 1])
                    index += 2
                    continue

            if char == '"':
                in_string = False

            index += 1
            continue

        if char == '"':
            in_string = True
            out.append(char)
            index += 1
            continue

        if char == '/':
            if index + 1 < length:

                # .. a line comment runs to the end of the line ..
                if text[index + 1] == '/':
                    end = text.find('\n', index)
                    if end == -1:
                        break
                    index = end
                    continue

                # .. and a block comment runs to its terminator.
                if text[index + 1] == '*':
                    end = text.find('*/', index + 2)
                    if end == -1:
                        raise ThemeConversionError(f'{name}: unterminated /* comment')
                    index = end + 2
                    continue

        out.append(char)
        index += 1

    result = ''.join(out)
    return result

# ################################################################################################################################

def _strip_trailing_commas(text:'str') -> 'str':
    """ Removes trailing commas before a closing brace or bracket - legal
    in JSONC, not in JSON.
    """
    out:'strlist' = []
    index = 0
    length = len(text)
    in_string = False

    while index < length:
        char = text[index]

        if in_string:
            out.append(char)

            if char == '\\':
                if index + 1 < length:
                    out.append(text[index + 1])
                    index += 2
                    continue

            if char == '"':
                in_string = False

            index += 1
            continue

        if char == '"':
            in_string = True
            out.append(char)
            index += 1
            continue

        if char == ',':

            # Look ahead past whitespace, drop the comma if a closer follows.
            ahead = index + 1
            while ahead < length:
                if text[ahead] not in ' \t\r\n':
                    break
                ahead += 1

            if ahead < length:
                if text[ahead] in '}]':
                    index += 1
                    continue

        out.append(char)
        index += 1

    result = ''.join(out)
    return result

# ################################################################################################################################

def strip_jsonc(text:'str', name:'str') -> 'str':
    """ Turns a JSONC document into plain JSON that json.loads can take.
    """
    without_comments = _strip_comments(text, name)

    out = _strip_trailing_commas(without_comments)
    return out

# ################################################################################################################################

def load_theme(path:'str') -> 'anydict':
    """ Loads a JSONC theme file, following its include chain. The
    including file's colors win over the included one's.
    """
    name = os.path.basename(path)

    with open(path) as theme_file:
        raw = theme_file.read()

    try:
        data = json.loads(strip_jsonc(raw, name))
    except json.JSONDecodeError as e:
        raise ThemeConversionError(f'{name}: not valid JSONC, {e}') from e

    colors:'anydict' = {}
    theme_type = data.get('type')
    theme_name = data.get('name')

    # An include is resolved relative to the file that names it and the
    # including file's own colors override the included ones.
    if 'include' in data:
        include_dir = os.path.dirname(path)
        include_path = os.path.join(include_dir, data['include'])
        included = load_theme(include_path)
        colors.update(included['colors'])
        if theme_type is None:
            theme_type = included['type']

    # The colors map itself is optional in the format, an included
    # skeleton file may carry none of its own.
    if own_colors := data.get('colors'):
        colors.update(own_colors)

    out = {'colors': colors, 'type': theme_type, 'name': theme_name}
    return out

# ################################################################################################################################
# ################################################################################################################################
