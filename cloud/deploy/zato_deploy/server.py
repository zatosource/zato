# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import ssl
from dataclasses import dataclass
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import parse_qs, urlsplit

# Zato
from zato_deploy.common import any_, Path, Port
from zato_deploy.state import Progress

# ################################################################################################################################
# ################################################################################################################################

_Progress_Path = '/zato-deploy/progress.json'
_Page_Name     = 'index.html'

# How long a connection may stay idle, including during its TLS handshake.
_Socket_Timeout = 30

# The files the page loads, by the path it asks for them under.
_Static_Files = {
    '/zato-deploy/fonts/Jost-Light.ttf':            ('fonts/Jost-Light.ttf',            'font/ttf'),
    '/zato-deploy/fonts/Jost-Regular.ttf':          ('fonts/Jost-Regular.ttf',          'font/ttf'),
    '/zato-deploy/fonts/Jost-Medium.ttf':           ('fonts/Jost-Medium.ttf',           'font/ttf'),
    '/zato-deploy/vendor/tippy/popperjs.core.js':   ('vendor/tippy/popperjs.core.js',   'text/javascript'),
    '/zato-deploy/vendor/tippy/tippy.js':           ('vendor/tippy/tippy.js',           'text/javascript'),
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StaticFile:
    content_type:  str
    cache_control: str
    content:       bytes

# ################################################################################################################################

strstaticdict = dict[str, StaticFile]

# ################################################################################################################################
# ################################################################################################################################

def _read_static_file(static_dir:'str', name:'str', content_type:'str', cache_control:'str') -> 'StaticFile':

    path = os.path.join(static_dir, name)

    with open(path, 'rb') as input_file:
        content = input_file.read()

    out = StaticFile()
    out.content_type  = content_type
    out.cache_control = cache_control
    out.content       = content

    return out

# ################################################################################################################################

def load_static_files(static_dir:'str') -> 'tuple[StaticFile, strstaticdict]':
    """ Returns the page and the files it loads, all read into memory up front.
    """
    page = _read_static_file(static_dir, _Page_Name, 'text/html; charset=utf-8', 'no-store')

    files:'strstaticdict' = {}

    for url_path, (name, content_type) in _Static_Files.items():
        files[url_path] = _read_static_file(static_dir, name, content_type, 'max-age=3600')

    out = (page, files)
    return out

# ################################################################################################################################
# ################################################################################################################################

class DeployServer(ThreadingHTTPServer):
    """ Serves the page and the progress over TLS until the Dashboard takes over the port.
    """
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        progress:'Progress',
        tls_context:'ssl.SSLContext',
        page:'StaticFile',
        static_files:'strstaticdict',
        ) -> 'None':

        self.progress     = progress
        self.tls_context  = tls_context
        self.page         = page
        self.static_files = static_files

        address = ('0.0.0.0', Port.Deploy)
        super().__init__(address, DeployHandler)

# ################################################################################################################################

    def finish_request(self, request:'any_', client_address:'any_') -> 'None':
        """ Runs the TLS handshake in the thread of each connection, so that a slow client holds up only itself.
        """
        raw_socket:'socket.socket' = request
        raw_socket.settimeout(_Socket_Timeout)

        try:
            tls_socket = self.tls_context.wrap_socket(raw_socket, server_side=True)
        except OSError:
            return

        try:
            super().finish_request(tls_socket, client_address)
        except OSError:
            pass
        finally:
            tls_socket.close()

# ################################################################################################################################
# ################################################################################################################################

class DeployHandler(BaseHTTPRequestHandler):
    """ Returns the progress under its own path and the page under every other one.
    """
    protocol_version = 'HTTP/1.1'
    server:'DeployServer'

    def do_GET(self) -> 'None':

        url = urlsplit(self.path)

        # The progress, with only the log lines after the last one the page has ..
        if url.path == _Progress_Path:
            query = parse_qs(url.query)
            after = 0
            if values := query.get('after'):
                if values[0].isdigit():
                    after = int(values[0])
            body = self.server.progress.to_json(after)
            self.send_body('application/json', 'no-store', body)

        # .. a file the page loads ..
        elif static_file := self.server.static_files.get(url.path):
            self.send_body(static_file.content_type, static_file.cache_control, static_file.content)

        # .. or the page itself, whichever address of the Dashboard was opened.
        else:
            page = self.server.page
            self.send_body(page.content_type, page.cache_control, page.content)

# ################################################################################################################################

    def send_body(self, content_type:'str', cache_control:'str', body:'bytes') -> 'None':

        content_length = len(body)

        self.send_response(OK)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(content_length))
        self.send_header('Cache-Control', cache_control)

        # Once the environment is ready, each request needs a new connection, which is what reaches the Dashboard in the end.
        if self.server.progress.is_ready:
            self.send_header('Connection', 'close')
            self.close_connection = True

        self.end_headers()

        _ = self.wfile.write(body)

# ################################################################################################################################

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

def start_server(progress:'Progress', pem_path:'str') -> 'DeployServer':
    """ Starts serving the page in a thread of its own and returns the server.
    """
    tls_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    tls_context.load_cert_chain(pem_path)

    page, static_files = load_static_files(Path.Static_Dir)

    out = DeployServer(progress, tls_context, page, static_files)

    thread = Thread(target=out.serve_forever, name='zato-deploy-server', daemon=True)
    thread.start()

    return out

# ################################################################################################################################
# ################################################################################################################################
