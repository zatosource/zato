# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The live proof - with the trace on, every exchange with the IMAP server, the SFTP server,
# the LLM and the SMTP receiver is printed as it happens, one channel tag per line and
# nothing else, so the run reads as a transcript rather than as a log.

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

# The environment variable that turns the trace on - any non-empty value does
Trace_Env_Key = 'Zato_Test_Explain_Trace'

# The channels a line may come from
Channel_IMAP    = 'IMAP'
Channel_SFTP    = 'SFTP'
Channel_LLM     = 'LLM'
Channel_SMTP    = 'SMTP'
Channel_Explain = 'EXPLAIN'

# What a line the test sent and one the server answered with open with
Sent     = '>>'
Received = '<<'

# What sets one exchange apart from the next
_separator = '-' * 100

# ################################################################################################################################
# ################################################################################################################################

def is_on() -> 'bool':
    """ Whether the trace is on - the variable is an outside boundary, so it is checked explicitly.
    """
    value = os.environ.get(Trace_Env_Key)

    if value is None:
        return False

    out = bool(value)
    return out

# ################################################################################################################################

def trace(channel:'str', direction:'str', text:'str') -> 'None':
    """ One exchange on one channel - a multi-line text keeps its lines, each under the same tag.
    """
    if not is_on():
        return

    prefix = f'[{channel}] {direction} '

    for line in text.rstrip('\n').split('\n'):
        print(prefix + line, flush=True)

# ################################################################################################################################

def separator(channel:'str') -> 'None':
    """ Closes one exchange on a channel.
    """
    if not is_on():
        return

    print(f'[{channel}] {_separator}', flush=True)

# ################################################################################################################################
# ################################################################################################################################
