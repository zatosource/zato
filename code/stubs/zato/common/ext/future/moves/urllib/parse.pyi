from typing import Any

from __future__ import absolute_import
from zato.common.ext.future.standard_library import suspend_hooks
from zato.common.ext.future.utils import PY3
from urllib.parse import *
from urlparse import ParseResult, SplitResult, parse_qs, parse_qsl, urldefrag, urljoin, urlparse, urlsplit, urlunparse, urlunsplit
from urllib import quote, quote_plus, unquote, unquote_plus, urlencode, splitquery
