# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The DNS server of a test session, run as a process of its own. It answers the queries for the A records of the names
# in its answers file and reads the file again for each query, so a test moves a name to another address by rewriting
# the file, the way the provider of a managed database service moves its endpoint name during a failover.
# The answers file has one line per name, with the name and its IPv4 address separated by a space.

# stdlib
import os
import socket
import struct
from argparse import ArgumentParser

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How long the resolvers may cache an answer, in seconds.
Answer_TTL = 5

# The largest UDP query that is read.
_query_size = 4096

# How often the server checks whether the process that started it still runs, in seconds.
_parent_check_interval = 1.0

# The fields of a DNS message.
_header_format = '>HHHHHH'
_header_size = 12
_question_tail_size = 4
_answer_format = '>HHIH'

# The flags of a response - a recursive response with recursion available, without or with the name error code.
_flags_found = 0x8180
_flags_not_found = 0x8183

# The type and the class of an A record of the internet class.
_type_a = 1
_class_in = 1

# A pointer to the name in the question, which starts right after the header.
_name_pointer = b'\xc0\x0c'

# The address that a host name is turned into for the IPv4 record.
_ipv4_address_size = 4

# ################################################################################################################################
# ################################################################################################################################

def read_answers(path:'str') -> 'strstrdict':
    """ Returns the names of the answers file, in lower case, with the addresses they resolve to.
    """
    out:'strstrdict' = {}

    with open(path) as answers_file:
        for line in answers_file:
            parts = line.split()
            if parts:
                name = parts[0].lower()
                out[name] = parts[1]

    return out

# ################################################################################################################################

def _read_question(query:'bytes') -> 'tuple[str, int, int]':
    """ Returns the name of the question of a query, the offset at which the question ends and the type it asks for.
    """
    labels:'list[str]' = []
    offset = _header_size

    while True:
        length = query[offset]
        offset += 1

        if length == 0:
            break

        label_end = offset + length
        label = query[offset:label_end]
        labels.append(label.decode('ascii'))
        offset = label_end

    question_type, _ = struct.unpack_from('>HH', query, offset)
    question_end = offset + _question_tail_size

    name = '.'.join(labels)
    name = name.lower()

    out = (name, question_end, question_type)
    return out

# ################################################################################################################################

def build_response(query:'bytes', answers:'strstrdict') -> 'bytes':
    """ Builds the response to one query - the address of a known name, no records for a known name asked for another
    type of record, and a name error for any other name.
    """
    message_id, = struct.unpack_from('>H', query, 0)
    name, question_end, question_type = _read_question(query)
    question = query[_header_size:question_end]

    record = b''

    if name in answers:
        flags = _flags_found

        if question_type == _type_a:
            address = socket.inet_aton(answers[name])
            record_header = struct.pack(_answer_format, _type_a, _class_in, Answer_TTL, _ipv4_address_size)
            record = _name_pointer + record_header + address

    else:
        flags = _flags_not_found

    if record:
        answer_count = 1
    else:
        answer_count = 0

    header = struct.pack(_header_format, message_id, flags, 1, answer_count, 0, 0)

    out = header + question + record
    return out

# ################################################################################################################################

def serve(server_socket:'socket.socket', answers_path:'str', parent_pid:'int') -> 'None':
    """ Answers the queries until the process that started the server ends.
    """
    server_socket.settimeout(_parent_check_interval)

    while True:

        # A server whose parent ended is no longer needed by anyone ..
        if os.getppid() != parent_pid:
            break

        # .. otherwise, it answers the next query, if there is one.
        try:
            query, client = server_socket.recvfrom(_query_size)
        except TimeoutError:
            continue

        answers = read_answers(answers_path)
        response = build_response(query, answers)
        _ = server_socket.sendto(response, client)

# ################################################################################################################################

def main() -> 'None':

    parser = ArgumentParser()
    _ = parser.add_argument('--answers-file', required=True)
    _ = parser.add_argument('--port-file', required=True)
    _ = parser.add_argument('--parent-pid', type=int, required=True)
    args = parser.parse_args()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('127.0.0.1', 0))
    port = server_socket.getsockname()[1]

    # The port is published only once the socket listens on it, through a file that appears in one step.
    temporary_path = args.port_file + '.tmp'

    with open(temporary_path, 'w') as port_file:
        _ = port_file.write(f'{port}')

    os.replace(temporary_path, args.port_file)

    serve(server_socket, args.answers_file, args.parent_pid)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
