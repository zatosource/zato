# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The stock runner helper - runs a Python module in its own interpreter and exposes the module's
functions over a local TCP socket, one JSON object per line. This file depends on the standard
library only, so any interpreter can run it directly by path:

    python /path/to/runner.py <port> <module-path>

Each request is one line - {"method": "...", "args": [...]} - and each response is one line too,
either {"result": ...} or {"error": "..."}.
"""

# stdlib
import json
import socket
import socketserver
import sys
from importlib.util import module_from_spec, spec_from_file_location

# ################################################################################################################################
# ################################################################################################################################

def load_module(module_path):
    """ Loads and returns the module the runner exposes, given its file path.
    """
    spec = spec_from_file_location('zato_runner_target', module_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# ################################################################################################################################
# ################################################################################################################################

class RunnerHandler(socketserver.StreamRequestHandler):
    """ Serves one connection - each request line names a function of the target module,
    the function is called and its result goes back as one response line.
    """
    def handle(self):
        for line in self.rfile:

            request = json.loads(line.decode('utf8'))

            try:
                function = getattr(self.server.runner_module, request['method'])
                result = function(*request['args'])
                response = {'result': result}
            except Exception as e:
                response = {'error': str(e)}

            _ = self.wfile.write((json.dumps(response) + '\n').encode('utf8'))
            self.wfile.flush()

# ################################################################################################################################
# ################################################################################################################################

class RunnerServer(socketserver.ThreadingTCPServer):
    """ The TCP server the runner listens on, holding the module it exposes.
    """
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, port, module):
        self.runner_module = module
        super().__init__(('127.0.0.1', port), RunnerHandler)

# ################################################################################################################################
# ################################################################################################################################

class RunnerClient:
    """ Talks to a runner process from the server side - a new connection per call keeps
    the client safe to share between concurrent calls.
    """
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def call(self, method, *args):

        request = json.dumps({'method': method, 'args': list(args)}) + '\n'

        # Connect for the duration of one call ..
        with socket.create_connection((self.host, self.port)) as conn:
            conn.sendall(request.encode('utf8'))

            # .. and read the one response line back.
            with conn.makefile('r', encoding='utf8') as reader:
                response = json.loads(reader.readline())

        # An error on the runner side becomes an exception on this side.
        if 'error' in response:
            raise Exception(response['error'])

        return response['result']

# ################################################################################################################################
# ################################################################################################################################

def main():
    port = int(sys.argv[1])
    module_path = sys.argv[2]

    module = load_module(module_path)

    server = RunnerServer(port, module)
    server.serve_forever()

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
