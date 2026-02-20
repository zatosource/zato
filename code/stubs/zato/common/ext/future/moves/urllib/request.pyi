from typing import Any, TYPE_CHECKING

from __future__ import absolute_import
from zato.common.ext.future.standard_library import suspend_hooks
from zato.common.ext.future.utils import PY3
from urllib.request import *
from urllib.request import getproxies, pathname2url, proxy_bypass, quote, request_host, thishost, unquote, url2pathname, urlcleanup, urljoin, urlopen, urlparse, urlretrieve, urlsplit, urlunparse
from urllib.parse import splitattr, splithost, splitpasswd, splitport, splitquery, splittag, splittype, splituser, splitvalue, to_bytes, unwrap
from urllib import *
from urllib2 import *
from urlparse import *
from urllib import toBytes

