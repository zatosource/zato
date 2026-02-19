from typing import Any

from __future__ import absolute_import
from zato.common.ext.future.standard_library import suspend_hooks
from zato.common.ext.future.utils import PY3
from urllib.error import *
from urllib import ContentTooShortError
from urllib2 import URLError, HTTPError
