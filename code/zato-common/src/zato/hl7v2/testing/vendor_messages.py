# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

_messages_root = os.environ['Zato_Health_Messages_Root']
_test_data_dir = Path(_messages_root) / 'hl7v2' / 'live'

# ################################################################################################################################
# ################################################################################################################################

# Markdown headers come in three forms - "## 1. ORM^O01 - wellness checkup order",
# "## 1. ORM^O01 with no dash in the title" and a bare "## 1".
# The message type part may contain spaces (e.g. "ORU R01"), so it is matched
# non-greedily up to the first dash.
_header_pattern         = re.compile(r'^## (\d+)\.\s+(.+?)\s*-\s*(.+)$')
_no_dash_header_pattern = re.compile(r'^## (\d+)\.\s+(.+)$')
_bare_header_pattern    = re.compile(r'^## (\d+)\s*$')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class VendorMessage:
    """ One numbered HL7 message from a vendor system, extracted from a markdown file.
    """
    number: 'int'
    message_type: 'str'
    description: 'str'
    er7: 'str'

# ################################################################################################################################
# ################################################################################################################################

vendor_message_list = list[VendorMessage]

# ################################################################################################################################
# ################################################################################################################################

def extract_messages(md_path:'Path') -> 'vendor_message_list':
    """ Parses a markdown file and returns a list of VendorMessage instances, one per numbered header found.
    """

    # Our response to produce
    out:'vendor_message_list' = []

    text = md_path.read_text(encoding='utf-8')
    lines = text.split('\n')

    line_count = len(lines)
    line_index = 0

    while line_index < line_count:
        line = lines[line_index]
        match = _header_pattern.match(line)
        no_dash_match = _no_dash_header_pattern.match(line)
        bare_match = _bare_header_pattern.match(line)

        if match:

            # We found a header like "## 1. ORM^O01 - wellness checkup order" ..
            number_text = match.group(1)
            description_text = match.group(3)

            message = VendorMessage()
            message.number = int(number_text)
            message.message_type = match.group(2)
            message.description = description_text.strip()

        elif no_dash_match:

            # .. or one with no dash, like "## 1. ORM^O01 with no dash in the title" ..
            number_text = no_dash_match.group(1)
            message_type_text = no_dash_match.group(2)

            message = VendorMessage()
            message.number = int(number_text)
            message.message_type = message_type_text.strip()
            message.description = ''

        elif bare_match:

            # .. or a bare header like "## 1" with no message type or description ..
            number_text = bare_match.group(1)

            message = VendorMessage()
            message.number = int(number_text)
            message.message_type = ''
            message.description = ''

        else:
            line_index += 1
            continue

        # .. now find the next fenced code block ..
        line_index += 1

        while line_index < line_count:
            if lines[line_index].startswith('```'):
                line_index += 1
                break
            line_index += 1

        # .. collect the ER7 lines until the closing fence ..
        er7_lines:'strlist' = []

        while line_index < line_count:
            if lines[line_index].startswith('```'):
                break
            er7_lines.append(lines[line_index])
            line_index += 1

        # .. and join them into a single wire-format message with carriage returns.
        joined = '\n'.join(er7_lines)
        stripped = joined.strip()
        message.er7 = stripped.replace('\n', '\r')

        out.append(message)
        line_index += 1

    return out

# ################################################################################################################################
# ################################################################################################################################

def load_message(md_path:'Path', number:'int') -> 'str':
    """ Extracts a single message by its number from a markdown file.
    """
    messages = extract_messages(md_path)

    for message in messages:

        # This is the message we are looking for.
        if message.number == number:
            break

    else:
        raise Exception(f'Message {number} not found in {md_path}.')

    out = message.er7
    return out

# ################################################################################################################################
# ################################################################################################################################

def md_path_for(land:'str', filename:'str') -> 'Path':
    """ Returns the full path to a markdown file under the test data directory.
    """
    out = _test_data_dir / land / filename
    return out

# ################################################################################################################################
# ################################################################################################################################

def md_path_for_vendor_file(filename:'str') -> 'Path':
    """ Returns the full path to a markdown file given its name alone - the name
    always begins with the name of the land directory that holds it.
    """
    candidates:'strlist' = []

    for item in _test_data_dir.iterdir():
        if item.is_dir():
            land_prefix = item.name + '-'
            if filename.startswith(land_prefix):
                candidates.append(item.name)

    # The longest directory name wins because one land name can be a prefix of another.
    land = max(candidates, key=len)

    out = _test_data_dir / land / filename
    return out

# ################################################################################################################################
# ################################################################################################################################
