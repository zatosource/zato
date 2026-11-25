# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HTTP server of zato_server_core in a process of its own. It listens on a TCP port, and on a Unix domain socket
# when the path of one is given, answers each request with a part of its request context in JSON and stops on SIGTERM.

# stdlib
import signal
import sys
from http.client import OK, responses
from json import dumps

# gevent
import gevent

# Zato
from zato_server_core.zato_server_core import HTTPServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple, strnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The interface of the TCP listener
    Host = '127.0.0.1'

    # The value of SERVER_SOFTWARE and the size limit of a request, in bytes
    Server_Software = 'Zato'
    Max_Msg_Size    = 1024 * 1024

    # The keys of the request context that a response returns
    Response_Keys = ('REMOTE_ADDR', 'REMOTE_PORT', 'PATH_INFO')

    # The status and the headers of each response
    Response_Status_Code = OK
    Response_Status      = f'{OK} {responses[OK]}'
    Response_Headers     = {'Content-Type': 'application/json'}

    # The lines that the process prints once both of its listeners accept connections and once the server stopped
    Ready_Line   = 'Listening'
    Stopped_Line = 'Stopped'

    # The positions of the command line arguments
    Port_Arg_Index        = 1
    Unix_Socket_Arg_Index = 2

# ################################################################################################################################
# ################################################################################################################################

def handle_request(request_ctx:'anydict') -> 'anytuple':
    """ Returns the part of the request context that the tests check.
    """
    body:'anydict' = {}

    for key in ModuleCtx.Response_Keys:
        body[key] = request_ctx[key]

    data = dumps(body).encode()

    out = (ModuleCtx.Response_Status, ModuleCtx.Response_Headers, data)
    return out

# ################################################################################################################################

def report_ready() -> 'None':
    """ Runs once the accept loop waits for the first time, by which time both listeners accept connections.
    """
    print(ModuleCtx.Ready_Line, flush=True)

# ################################################################################################################################

def main() -> 'None':

    # The port is always given, the path of the Unix domain socket only for a server that listens on one ..
    port = int(sys.argv[ModuleCtx.Port_Arg_Index])

    arg_count = len(sys.argv)
    has_unix_socket = arg_count > ModuleCtx.Unix_Socket_Arg_Index

    unix_socket_path:'strnone' = None

    if has_unix_socket:
        unix_socket_path = sys.argv[ModuleCtx.Unix_Socket_Arg_Index]

    # .. the server is created ..
    bind_address = (ModuleCtx.Host, port)
    server = HTTPServer(bind_address, handle_request, ModuleCtx.Server_Software, ModuleCtx.Max_Msg_Size, unix_socket_path)

    # .. SIGTERM stops it from a greenlet of its own ..
    def on_sigterm() -> 'None':
        _ = gevent.spawn(server.stop)

    _ = gevent.signal_handler(signal.SIGTERM, on_sigterm)

    # .. the process reports when it is ready ..
    _ = gevent.spawn(report_ready)

    # .. and it serves until it is stopped.
    server.serve_forever()

    print(ModuleCtx.Stopped_Line, flush=True)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
