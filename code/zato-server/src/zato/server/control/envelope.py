# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The messages of the control channel between the arbiter and its workers. Each message is one SEQPACKET datagram
# that holds a JSON header, a newline and a JSON body. The header holds a type, a sequence number assigned by the arbiter,
# the originating slot, the target slot and a correlation ID, so the arbiter routes a message without reading its body.
# A body above a named size is written to a file, the header holds the path of the file instead, and the reader
# of the body removes it.

# stdlib
import os
from dataclasses import dataclass
from json import dumps, loads
from uuid import uuid4

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, tuple_

    any_ = any_
    anydict = anydict

    headerbody = tuple_['anydict', bytes]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # A body larger than this, in bytes of its JSON form, is written to a file
    Max_Inline_Body = 65536

    # The largest header of a datagram, in bytes
    Max_Header = 4096

    # The largest datagram that a receiver reads
    Max_Datagram = Max_Inline_Body + Max_Header

    # The prefix of the files that hold bodies above the inline size
    Body_File_Prefix = 'zato-control-'

    # Separates the header of a datagram from its body, and JSON without indentation never contains it
    Separator = b'\n'

    # The value of the sequence number and of the slot before the arbiter assigns them
    No_Sequence = 0
    No_Slot     = -1

# ################################################################################################################################
# ################################################################################################################################

class MessageType:
    Event        = 'event'
    Ready        = 'ready'
    Query        = 'query'
    Response     = 'response'
    Query_Result = 'query-result'
    Drain        = 'drain'
    Reload       = 'reload'

    # The arbiter renamed log files and asks a worker to reopen them, which the worker acknowledges with the rotation ID
    Reopen_Logs   = 'reopen-logs'
    Logs_Reopened = 'logs-reopened'

    # A process learned that another server took over the pub/sub database, after which the arbiter drains its processes
    Replaced = 'replaced'

    # The worker forwards an invocation of a service that changes configuration to the config process,
    # which returns its result to the worker after the events of the change
    Forward        = 'forward'
    Forward_Result = 'forward-result'

    # The worker asks the config process for a load of its configuration, the config process sends a mark to the worker
    # once no change is in progress, and the worker reports that it loaded its configuration
    Load_Request = 'load-request'
    Mark         = 'mark'
    Load_Done    = 'load-done'

    # The arbiter tells the config process whether it waits for a load of the worker and that the worker terminated
    Loading_State = 'loading-state'
    Worker_Gone   = 'worker-gone'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Message:
    """ One message of the control channel.
    """
    type:   'str'
    seq:    'int'
    slot:   'int'
    target: 'int'
    cid:    'str'
    body:   'any_'

# ################################################################################################################################
# ################################################################################################################################

def new_cid() -> 'str':
    out = uuid4().hex
    return out

# ################################################################################################################################

def new_message(type:'str', body:'any_', cid:'str'='', target:'int'=ModuleCtx.No_Slot) -> 'Message':
    """ Returns a message that the arbiter has not assigned a sequence number or a slot to yet,
    addressed to the slot of a target if the message is sent to one slot only.
    """
    out = Message()
    out.type   = type
    out.seq    = ModuleCtx.No_Sequence
    out.slot   = ModuleCtx.No_Slot
    out.target = target
    out.cid    = cid
    out.body   = body

    return out

# ################################################################################################################################

def new_body_path(body_dir:'str') -> 'str':
    file_name = ModuleCtx.Body_File_Prefix + new_cid()
    out = os.path.join(body_dir, file_name)
    return out

# ################################################################################################################################

def join(header:'anydict', body:'bytes') -> 'bytes':
    """ Returns the datagram of a header and a body.
    """
    header_json = dumps(header)
    header_bytes = header_json.encode('utf8')

    out = header_bytes + ModuleCtx.Separator + body
    return out

# ################################################################################################################################

def split(datagram:'bytes') -> 'headerbody':
    """ Returns the header of a datagram and its body, which is empty when the body is in a file.
    """
    header_bytes, _, body = datagram.partition(ModuleCtx.Separator)
    header = loads(header_bytes)

    out = header, body
    return out

# ################################################################################################################################

def encode(message:'Message', body_dir:'str') -> 'bytes':
    """ Returns the datagram of a message, writing its body to a file under a directory when the body is too large.
    """
    body_json = dumps(message.body)
    body = body_json.encode('utf8')

    header:'anydict' = {
        'type': message.type,
        'seq': message.seq,
        'slot': message.slot,
        'target': message.target,
        'cid': message.cid,
    }

    # A large body is in a file of its own, which the header names.
    if len(body) > ModuleCtx.Max_Inline_Body:
        path = new_body_path(body_dir)

        with open(path, 'wb') as body_file:
            _ = body_file.write(body)

        header['path'] = path
        body = b''

    out = join(header, body)
    return out

# ################################################################################################################################

def decode(datagram:'bytes') -> 'Message':
    """ Returns the message of a datagram, reading its body from a file and removing the file if the header names one.
    """
    header, body = split(datagram)

    if path := header.get('path'):
        with open(path, 'rb') as body_file:
            body = body_file.read()
        os.remove(path)

    out = Message()
    out.type = header['type']
    out.seq  = header['seq']
    out.slot   = header['slot']
    out.target = header['target']
    out.cid    = header['cid']
    out.body   = loads(body)

    return out

# ################################################################################################################################
# ################################################################################################################################
