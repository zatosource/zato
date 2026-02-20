from typing import Any, TYPE_CHECKING

import sys
from zato.server.ext.zunicorn import six
from zato.common.py23_.past.builtins import execfile, unicode
import inspect
from importlib.util import find_spec as find_module
from os.path import realpath, dirname, basename, splitext
import urllib.parse
import urllib
import builtins
import errno
import select
import socket
from urlparse import _parse_cache, MAX_CACHE_SIZE, clear_cache, _splitnetloc, SplitResult, scheme_chars
from urllib.parse import urlsplit
import html
import marshal
import cgi

urlsplit = urlsplit

def _check_if_pyc(fname: Any) -> None: ...

def _get_codeobj(pyfile: Any) -> None: ...

def _wrap_error(exc: Any, mapping: Any, key: Any) -> None: ...
