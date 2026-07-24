# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Loading of VS Code color theme files: they are JSONC (comments and
# trailing commas allowed) and may include one another, the including
# file's colors winning over the included one's.

# stdlib
import json
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

def _strip_comments(text:'str', name:'str') -> 'str':
    """ Removes // and /* */ comments outside strings. A tiny scanner
    rather than a regex, because values like vscode://schemas contain slashes.
    """
    out = []
    index = 0
    length = len(text)
    in_string = False

    # Walk the text once, copying everything that is not a comment ..
    while index < length:
        char = text[index]

        if in_string:
            out.append(char)

            # .. a backslash escapes the next character, including a quote ..
            if char == '\\' and index + 1 < length:
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

        # .. a line comment runs to the end of the line ..
        if char == '/' and index + 1 < length and text[index + 1] == '/':
            end = text.find('\n', index)
            if end == -1:
                break
            index = end
            continue

        # .. and a block comment runs to its terminator.
        if char == '/' and index + 1 < length and text[index + 1] == '*':
            end = text.find('*/', index + 2)
            if end == -1:
                raise SystemExit(f'{name}: unterminated /* comment')
            index = end + 2
            continue

        out.append(char)
        index += 1

    result = ''.join(out)
    return result

# ################################################################################################################################

def _strip_trailing_commas(text:'str') -> 'str':
    """ Trailing commas before a closing brace or bracket are legal in
    JSONC, not in JSON, so they go too.
    """
    out = []
    in_string = False
    index = 0
    length = len(text)

    while index < length:
        char = text[index]

        if in_string:
            out.append(char)
            if char == '\\' and index + 1 < length:
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
            while ahead < length and text[ahead] in ' \t\r\n':
                ahead += 1
            if ahead < length and text[ahead] in '}]':
                index += 1
                continue

        out.append(char)
        index += 1

    result = ''.join(out)
    return result

# ################################################################################################################################

def strip_jsonc(text:'str', name:'str') -> 'str':
    """ Removes comments and trailing commas so json.loads can take the result.
    """
    without_comments = _strip_comments(text, name)

    out = _strip_trailing_commas(without_comments)
    return out

# ################################################################################################################################

def load_theme(path:'str') -> 'stranydict':
    """ Loads a JSONC theme file, following its include chain. The
    including file's colors win over the included one's.
    """
    name = os.path.basename(path)
    with open(path) as file_object:
        raw = file_object.read()

    try:
        data = json.loads(strip_jsonc(raw, name))
    except json.JSONDecodeError as e:
        raise SystemExit(f'{name}: not valid JSONC, {e}') from e

    colors = {}
    theme_type = data.get('type')
    theme_name = data.get('name')

    # An include is resolved relative to the file that names it and the
    # including file's own colors override the included ones.
    if 'include' in data:
        included_path = os.path.join(os.path.dirname(path), data['include'])
        included = load_theme(included_path)
        colors.update(included['colors'])
        if theme_type is None:
            theme_type = included['type']

    # The colors map is genuinely optional - include-only files may carry none.
    if own_colors := data.get('colors'):
        colors.update(own_colors)

    out = {'colors': colors, 'type': theme_type, 'name': theme_name}
    return out

# ################################################################################################################################
# ################################################################################################################################
