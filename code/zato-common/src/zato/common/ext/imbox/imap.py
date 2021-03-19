"""
This module is a modified vendor copy of the Imbox package from https://pypi.org/project/imbox/

The MIT License (MIT)

Copyright (c) 2013 Martin Rusev

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from imaplib import IMAP4, IMAP4_SSL

import logging
import ssl as pythonssllib

logger = logging.getLogger(__name__)


class ImapTransport:

    def __init__(self, hostname, port=None, ssl=True, ssl_context=None, starttls=False):
        self.hostname = hostname

        if ssl:
            self.port = port or 993
            if ssl_context is None:
                ssl_context = pythonssllib.create_default_context()
            self.server = IMAP4_SSL(self.hostname, self.port, ssl_context=ssl_context)
        else:
            self.port = port or 143
            self.server = IMAP4(self.hostname, self.port)

        if starttls:
            self.server.starttls()
        logger.debug("Created IMAP4 transport for {host}:{port}".format(host=self.hostname, port=self.port))

    def list_folders(self):
        logger.debug("List all folders in mailbox")
        return self.server.list()

    def connect(self, username, password):
        self.server.login(username, password)
        self.server.select()
        logger.debug("Logged into server {} and selected mailbox 'INBOX'"
                     .format(self.hostname))
        return self.server
