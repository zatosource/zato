from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
import sys
from threading import Thread
from zato.common.ext.future.utils import PY2
from itertools import ifilter
from itertools import izip
from cPickle import dumps as pickle_dumps
from cPickle import loads as pickle_loads
from pickle import dumps as pickle_dumps
from pickle import loads as pickle_loads

def start_new_thread(target: Any, args: Any) -> None: ...
