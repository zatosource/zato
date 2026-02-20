from typing import Any, TYPE_CHECKING

import imaplib
import io
import re
import email
import chardet
import base64
import quopri
import sys
import time
from datetime import datetime
from email.header import decode_header
from zato.common.ext.imbox.utils import str_encode, str_decode
import logging


class Struct:
    def __init__(self: Any, **entries: Any) -> None: ...
    def keys(self: Any) -> None: ...
    def __repr__(self: Any) -> None: ...

def decode_mail_header(value: Any, default_charset: Any = ...) -> None: ...

def get_mail_addresses(message: Any, header_name: Any) -> None: ...

def decode_param(param: Any) -> None: ...

def parse_attachment(message_part: Any) -> None: ...

def decode_content(message: Any) -> None: ...

def fetch_email_by_uid(uid: Any, connection: Any, parser_policy: Any) -> None: ...

def parse_flags(headers: Any) -> None: ...

def parse_email(raw_email: Any, policy: Any = ...) -> None: ...
