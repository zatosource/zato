# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import tempfile
from json import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

# Where the per-test wire log files live - outside the quickstart temp directory,
# so they survive the suite's teardown and can be read after a failed run.
_wire_directory = os.path.join(tempfile.gettempdir(), 'zato_mcp_llm_live_wire')

# How many trailing lines of the Ollama container log go into the failure dump
_ollama_log_tail = '200'

# The container whose log is dumped on failure
_ollama_container = 'zato-test-ollama'

# The extensions of the wire log file and of the Ollama log dump next to it
_wire_suffix   = '.txt'
_ollama_suffix = '.ollama.txt'

# The wire log file of the test currently running, set by the conftest fixture
_current_path:'strnone' = None

# The wire entries of the test currently running, in order - the tests that assert
# on their own traffic read them back through get_entries.
_current_entries:'dictlist' = []

# ################################################################################################################################
# ################################################################################################################################

def _sanitize_node_id(node_id:'str') -> 'str':
    """ Turns a pytest node id into a file name.
    """

    characters:'strlist' = []

    for character in node_id:
        if character.isalnum():
            characters.append(character)
        elif character in '.-_':
            characters.append(character)
        else:
            characters.append('_')

    out = ''.join(characters)
    return out

# ################################################################################################################################

def set_current_test(node_id:'str') -> 'None':
    """ Points the wire log at a fresh file named after the test that is about to run.
    """

    global _current_path

    os.makedirs(_wire_directory, exist_ok=True)

    file_name = _sanitize_node_id(node_id) + _wire_suffix
    _current_path = os.path.join(_wire_directory, file_name)

    _current_entries.clear()

    # A rerun of the same test starts with an empty file.
    with open(_current_path, 'w') as wire_file:
        _ = wire_file.write('')

# ################################################################################################################################

def clear_current_test() -> 'None':
    """ Detaches the wire log once the test is over.
    """

    global _current_path
    _current_path = None

    _current_entries.clear()

# ################################################################################################################################

def get_entries(kind:'strnone' = None) -> 'dictlist':
    """ The wire entries of the test currently running, in order,
    optionally narrowed to one kind.
    """

    out:'dictlist' = []

    for entry in _current_entries:

        if kind is None:
            out.append(entry)
        elif entry['kind'] == kind:
            out.append(entry)

    return out

# ################################################################################################################################

def get_current_path() -> 'strnone':
    """ The wire log file of the test currently running, if any.
    """

    out = _current_path
    return out

# ################################################################################################################################

def write_entry(kind:'str', payload:'any_') -> 'None':
    """ Appends one pretty-printed wire event to the current test's log file.
    """

    if not _current_path:
        return

    document = {'kind': kind, 'payload': payload}
    _current_entries.append(document)

    text = dumps(document, indent=2, default=str)

    with open(_current_path, 'a') as wire_file:
        _ = wire_file.write(text)
        _ = wire_file.write('\n')

# ################################################################################################################################

def dump_ollama_logs() -> 'strnone':
    """ Writes the tail of the Ollama container log next to the current test's wire log
    and returns the path of the dump, or None when there is nothing to write to.
    """

    if not _current_path:
        out = None
        return out

    command = ['docker', 'logs', '--tail', _ollama_log_tail, _ollama_container]
    result = subprocess.run(command, capture_output=True, text=True)

    wire_suffix_length = len(_wire_suffix)
    dump_base = _current_path[:-wire_suffix_length]
    dump_path = dump_base + _ollama_suffix

    with open(dump_path, 'w') as dump_file:
        _ = dump_file.write(result.stdout)
        _ = dump_file.write(result.stderr)

    out = dump_path
    return out

# ################################################################################################################################
# ################################################################################################################################
