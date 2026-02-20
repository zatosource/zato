from typing import Any, TYPE_CHECKING

import logging
import ssl as pythonssllib
from imaplib import IMAP4, IMAP4_SSL


class ImapTransport:
    hostname: Any
    port: Any
    server: IMAP4
    def __init__(self: Any, hostname: Any, port: Any = ..., ssl: Any = ..., ssl_context: Any = ..., starttls: Any = ...) -> None: ...
    def list_folders(self: Any) -> None: ...
    def connect(self: Any, username: Any, password: Any) -> None: ...
