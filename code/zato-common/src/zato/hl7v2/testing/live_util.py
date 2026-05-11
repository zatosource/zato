# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

current = Path(__file__).resolve().parent
while current.name != 'code':
    current = current.parent
_test_data_dir = current / 'tests' / 'messages' / 'hl7v2' / 'live'

# ################################################################################################################################
# ################################################################################################################################

_header_pattern = re.compile(r'^## (\d+)\.\s+(\S+)\s*-\s*(.+)$')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LiveMessage:
    number: 'int'
    message_type: 'str'
    description: 'str'
    raw_er7: 'str'

# ################################################################################################################################
# ################################################################################################################################

live_message_list = list[LiveMessage]

# ################################################################################################################################
# ################################################################################################################################

def extract_messages(md_path:'Path') -> 'live_message_list':
    """ Parse a .md file and return a list of LiveMessage instances,
    one per numbered example found in the file.
    """

    # Our response to produce
    out:'live_message_list' = []

    text = md_path.read_text(encoding='utf-8')
    lines = text.split('\n')

    line_count = len(lines)
    line_idx = 0

    while line_idx < line_count:
        line = lines[line_idx]
        match = _header_pattern.match(line)

        if match:

            # We found a header like "## 1. ORM^O01 - CT abdomen order" ..
            message = LiveMessage()
            message.number = int(match.group(1))
            message.message_type = match.group(2)
            message.description = match.group(3).strip()

            # .. now find the next fenced code block ..
            line_idx += 1

            while line_idx < line_count:
                if lines[line_idx].startswith('```'):
                    line_idx += 1
                    break
                line_idx += 1

            # .. collect the ER7 lines until the closing fence ..
            er7_lines:'list[str]' = []

            while line_idx < line_count:
                if lines[line_idx].startswith('```'):
                    break
                er7_lines.append(lines[line_idx])
                line_idx += 1

            raw = '\n'.join(er7_lines).strip().replace('\n', '\r')
            message.raw_er7 = raw

            out.append(message)

        line_idx += 1

    return out

# ################################################################################################################################
# ################################################################################################################################

def load_message(md_path:'Path', number:'int') -> 'str':
    """ Extract a single example by its number from a .md file.
    """

    messages = extract_messages(md_path)

    for message in messages:
        if message.number == number:

            out = message.raw_er7
            return out

    raise ValueError(f'Example {number} not found in {md_path}')

# ################################################################################################################################
# ################################################################################################################################

def md_path_for(land:'str', filename:'str') -> 'Path':
    """ Return the full path to a .md file under the live test data directory.
    """

    out = _test_data_dir / land / filename
    return out

# ################################################################################################################################
# ################################################################################################################################
