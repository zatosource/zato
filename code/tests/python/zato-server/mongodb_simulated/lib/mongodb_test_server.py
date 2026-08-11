# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import socketserver
import threading
from datetime import datetime, timezone
from struct import pack, unpack_from

# PyMongo
from bson import decode as bson_decode, encode as bson_encode
from bson.int64 import Int64

# Zato
from zato.common.typing_ import dictlist

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# One in-memory collection is a list of documents, keyed by database and collection name
collectionkey  = tuple[str, str]
collectiondict = dict[collectionkey, dictlist]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Where the server listens
    Host = '127.0.0.1'

    # Wire protocol opcodes
    Op_Reply = 1
    Op_Query = 2004
    Op_Msg   = 2013

    # Every message starts with four int32 fields
    Header_Length = 16

    # OP_MSG flag bits
    Flag_Checksum_Present = 1
    Flag_More_To_Come     = 2

    # OP_MSG section kinds
    Section_Body              = 0
    Section_Document_Sequence = 1

    # What the hello response advertises
    Min_Wire_Version = 0
    Max_Wire_Version = 21
    Max_BSON_Object_Size = 16 * 1024 * 1024
    Max_Message_Size_Bytes = 48_000_000
    Max_Write_Batch_Size = 100_000
    Logical_Session_Timeout_Minutes = 30

    # What buildInfo reports
    Server_Version = '7.0.0'
    Server_Version_Array = [7, 0, 0, 0]

    # The error code of an unrecognized command
    Command_Not_Found_Code = 59

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Returns a TCP port that is free right now.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ModuleCtx.Host, 0))
        _, port = sock.getsockname()

    return port

# ################################################################################################################################
# ################################################################################################################################

def _read_exact(connection:'any_', size:'int') -> 'bytes | None':
    """ Reads exactly the given number of bytes from a socket, or None if the peer closed it.
    """
    data = b''
    remaining = size

    while remaining:
        chunk = connection.recv(remaining)

        # An empty chunk means the peer closed the connection
        if not chunk:
            return None

        data += chunk
        remaining = size - len(data)

    return data

# ################################################################################################################################

def _matches(document:'anydict', query:'anydict') -> 'bool':
    """ Returns True if the document matches every top-level equality condition of the query.
    """
    for key, expected in query.items():

        # A missing key can never match
        if key not in document:
            out = False
            break

        # A different value does not match either
        if document[key] != expected:
            out = False
            break

    else:
        out = True

    return out

# ################################################################################################################################

def _apply_update(document:'anydict', update_document:'anydict') -> 'bool':
    """ Applies a $set update or a full replacement to a document, returning True if anything changed.
    """
    out = False

    # A $set update assigns the given fields ..
    if set_fields := update_document.get('$set'):
        for key, value in set_fields.items():

            if key in document:
                if document[key] == value:
                    continue

            document[key] = value
            out = True

    # .. anything without operators is a full replacement that keeps the _id.
    else:
        document_id = document['_id']
        document.clear()
        document['_id'] = document_id
        document.update(update_document)
        out = True

    return out

# ################################################################################################################################
# ################################################################################################################################

def _command_hello(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    """ Answers the handshake and monitoring hello commands.
    """
    with server.lock:
        server.connection_count += 1
        connection_id = server.connection_count

    local_time = datetime.now(timezone.utc)

    out = {
        'helloOk': True,
        'ismaster': True,
        'isWritablePrimary': True,
        'maxBsonObjectSize': ModuleCtx.Max_BSON_Object_Size,
        'maxMessageSizeBytes': ModuleCtx.Max_Message_Size_Bytes,
        'maxWriteBatchSize': ModuleCtx.Max_Write_Batch_Size,
        'localTime': local_time,
        'logicalSessionTimeoutMinutes': ModuleCtx.Logical_Session_Timeout_Minutes,
        'connectionId': connection_id,
        'minWireVersion': ModuleCtx.Min_Wire_Version,
        'maxWireVersion': ModuleCtx.Max_Wire_Version,
        'readOnly': False,
        'ok': 1.0,
    }
    return out

# ################################################################################################################################

def _command_ping(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    out = {'ok': 1.0}
    return out

# ################################################################################################################################

def _command_build_info(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    out = {
        'version': ModuleCtx.Server_Version,
        'versionArray': ModuleCtx.Server_Version_Array,
        'ok': 1.0,
    }
    return out

# ################################################################################################################################

def _command_insert(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    """ Appends the given documents to the collection.
    """
    database_name = body['$db']
    collection_name = body['insert']
    documents = body['documents']

    inserted_count = len(documents)

    with server.lock:
        collection = server.collections.setdefault((database_name, collection_name), [])

        for document in documents:
            collection.append(document)

    out = {'n': inserted_count, 'ok': 1.0}
    return out

# ################################################################################################################################

def _command_find(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    """ Returns the documents matching the filter, all of them in the first batch.
    """
    database_name = body['$db']
    collection_name = body['find']
    query = body['filter']

    with server.lock:
        collection = server.collections.setdefault((database_name, collection_name), [])

        matching_documents:'dictlist' = []

        for document in collection:
            if _matches(document, query):
                matching_documents.append(document)

    # A limit is present only when the client asked for one
    if limit := body.get('limit'):
        matching_documents = matching_documents[:limit]

    namespace = f'{database_name}.{collection_name}'

    out = {
        'cursor': {
            'firstBatch': matching_documents,
            'id': Int64(0),
            'ns': namespace,
        },
        'ok': 1.0,
    }
    return out

# ################################################################################################################################

def _command_update(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    """ Applies each update statement to the documents its query matches.
    """
    database_name = body['$db']
    collection_name = body['update']
    updates = body['updates']

    matched_count = 0
    modified_count = 0

    with server.lock:
        collection = server.collections.setdefault((database_name, collection_name), [])

        for update_spec in updates:
            query = update_spec['q']
            update_document = update_spec['u']
            is_multi = update_spec['multi']

            for document in collection:

                if not _matches(document, query):
                    continue

                matched_count += 1

                if _apply_update(document, update_document):
                    modified_count += 1

                if not is_multi:
                    break

    out = {'n': matched_count, 'nModified': modified_count, 'ok': 1.0}
    return out

# ################################################################################################################################

def _command_delete(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    """ Deletes the documents each delete statement matches, honoring its limit.
    """
    database_name = body['$db']
    collection_name = body['delete']
    deletes = body['deletes']

    deleted_count = 0

    with server.lock:
        collection = server.collections.setdefault((database_name, collection_name), [])

        for delete_spec in deletes:
            query = delete_spec['q']
            limit = delete_spec['limit']

            remaining_documents:'dictlist' = []
            deleted_here = 0

            for document in collection:

                # A limit of zero means all the matching documents go away
                may_delete_more = limit == 0 or deleted_here < limit

                if may_delete_more:
                    if _matches(document, query):
                        deleted_here += 1
                        continue

                remaining_documents.append(document)

            collection[:] = remaining_documents
            deleted_count += deleted_here

    out = {'n': deleted_count, 'ok': 1.0}
    return out

# ################################################################################################################################

def _command_get_more(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    """ Every find returns its whole result in the first batch, so there is never more to get.
    """
    database_name = body['$db']
    collection_name = body['collection']

    namespace = f'{database_name}.{collection_name}'

    out = {
        'cursor': {
            'nextBatch': [],
            'id': Int64(0),
            'ns': namespace,
        },
        'ok': 1.0,
    }
    return out

# ################################################################################################################################

def _command_kill_cursors(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    out = {
        'cursorsKilled': body['cursors'],
        'cursorsNotFound': [],
        'cursorsAlive': [],
        'ok': 1.0,
    }
    return out

# ################################################################################################################################

def _command_end_sessions(server:'MongoDBTestServer', body:'anydict') -> 'anydict':
    out = {'ok': 1.0}
    return out

# ################################################################################################################################
# ################################################################################################################################

_command_handlers = {
    'hello':       _command_hello,
    'ismaster':    _command_hello,
    'isMaster':    _command_hello,
    'ping':        _command_ping,
    'buildInfo':   _command_build_info,
    'buildinfo':   _command_build_info,
    'insert':      _command_insert,
    'find':        _command_find,
    'update':      _command_update,
    'delete':      _command_delete,
    'getMore':     _command_get_more,
    'killCursors': _command_kill_cursors,
    'endSessions': _command_end_sessions,
}

# ################################################################################################################################
# ################################################################################################################################

class MongoDBTestHandler(socketserver.BaseRequestHandler):
    """ Speaks the MongoDB wire protocol with one client connection - the handshake arrives
    as OP_QUERY and everything after it as OP_MSG.
    """

    server:'MongoDBTestServer'

    def handle(self) -> 'None':

        while True:

            # Each message starts with a fixed-size header ..
            header = _read_exact(self.request, ModuleCtx.Header_Length)

            if header is None:
                break

            message_length, request_id, _response_to, op_code = unpack_from('<iiii', header)

            # .. followed by the rest of the message ..
            remaining_length = message_length - ModuleCtx.Header_Length
            payload = _read_exact(self.request, remaining_length)

            if payload is None:
                break

            # .. which is dispatched on its opcode.
            if op_code == ModuleCtx.Op_Query:
                reply = self._handle_op_query(payload, request_id)

            else:
                reply = self._handle_op_msg(payload, request_id)

            # No reply is expected when the client fired and forgot
            if reply is not None:
                self.request.sendall(reply)

# ################################################################################################################################

    def _next_request_id(self) -> 'int':
        with self.server.lock:
            self.server.request_count += 1
            out = self.server.request_count

        return out

# ################################################################################################################################

    def _handle_op_query(self, payload:'bytes', request_id:'int') -> 'bytes':
        """ Answers an OP_QUERY message - the client only ever sends the handshake hello this way.
        """

        # The collection name is a zero-terminated string after the flags
        name_end = payload.index(0, 4)

        # The query document follows the numberToSkip and numberToReturn fields
        document_offset = name_end + 1 + 4 + 4
        document_length = unpack_from('<i', payload, document_offset)[0]
        document_bytes = payload[document_offset:document_offset + document_length]
        body = bson_decode(document_bytes)

        reply_document = _command_hello(self.server, body)
        reply_document_bytes = bson_encode(reply_document)

        # An OP_REPLY carries its flags, cursor id, starting position and document count
        reply_body = pack('<iqii', 0, 0, 0, 1) + reply_document_bytes

        reply_length = ModuleCtx.Header_Length + len(reply_body)
        reply_request_id = self._next_request_id()
        reply_header = pack('<iiii', reply_length, reply_request_id, request_id, ModuleCtx.Op_Reply)

        out = reply_header + reply_body
        return out

# ################################################################################################################################

    def _handle_op_msg(self, payload:'bytes', request_id:'int') -> 'bytes | None':
        """ Decodes an OP_MSG command, runs it and builds the OP_MSG reply.
        """
        flag_bits = unpack_from('<I', payload, 0)[0]

        # An optional checksum trails the sections
        end = len(payload)

        if flag_bits & ModuleCtx.Flag_Checksum_Present:
            end -= 4

        body:'anydict' = {}
        offset = 4

        # Walk all the sections - the body document and any document sequences ..
        while offset < end:

            kind = payload[offset]
            offset += 1

            # .. the body is a single document ..
            if kind == ModuleCtx.Section_Body:
                document_length = unpack_from('<i', payload, offset)[0]
                document_bytes = payload[offset:offset + document_length]
                body.update(bson_decode(document_bytes))
                offset += document_length

            # .. a sequence carries its size, its field name and then the documents,
            # .. and it lands in the body under that field name, e.g. documents or updates.
            else:
                section_size = unpack_from('<i', payload, offset)[0]
                section_end = offset + section_size

                cursor = offset + 4
                identifier_end = payload.index(0, cursor)
                identifier = payload[cursor:identifier_end].decode('utf8')
                cursor = identifier_end + 1

                documents:'dictlist' = []

                while cursor < section_end:
                    document_length = unpack_from('<i', payload, cursor)[0]
                    document_bytes = payload[cursor:cursor + document_length]
                    documents.append(bson_decode(document_bytes))
                    cursor += document_length

                body[identifier] = documents
                offset = section_end

        # The command's name is always the first key of the body
        command_name = next(iter(body))

        if handler := _command_handlers.get(command_name):
            reply_document = handler(self.server, body)
        else:
            reply_document = {
                'ok': 0.0,
                'errmsg': f'no such command: {command_name}',
                'code': ModuleCtx.Command_Not_Found_Code,
                'codeName': 'CommandNotFound',
            }

        # The client does not want a reply to a fire-and-forget message
        if flag_bits & ModuleCtx.Flag_More_To_Come:
            return None

        reply_document_bytes = bson_encode(reply_document)
        reply_body = pack('<I', 0) + pack('<B', ModuleCtx.Section_Body) + reply_document_bytes

        reply_length = ModuleCtx.Header_Length + len(reply_body)
        reply_request_id = self._next_request_id()
        reply_header = pack('<iiii', reply_length, reply_request_id, request_id, ModuleCtx.Op_Msg)

        out = reply_header + reply_body
        return out

# ################################################################################################################################
# ################################################################################################################################

class MongoDBTestServer(socketserver.ThreadingTCPServer):
    """ A TCP server that pymongo clients connect to the same way they connect to a real MongoDB,
    with an in-memory dict of collections behind the commands.
    """
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address:'any_', handler_class:'any_') -> 'None':
        super().__init__(address, handler_class)

        self.lock = threading.Lock()

        # Documents keyed by (database name, collection name)
        self.collections:'collectiondict' = {}

        self.connection_count = 0
        self.request_count = 0

# ################################################################################################################################
# ################################################################################################################################

def start_mongodb_test_server(port:'int') -> 'MongoDBTestServer':
    """ Starts the server on the given port, serving in a daemon thread.
    """
    out = MongoDBTestServer((ModuleCtx.Host, port), MongoDBTestHandler)

    thread = threading.Thread(target=out.serve_forever, daemon=True)
    thread.start()

    return out

# ################################################################################################################################
# ################################################################################################################################
