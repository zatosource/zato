from typing import Any, TYPE_CHECKING

import os
from datetime import datetime
from itertools import groupby
from io import StringIO
from operator import attrgetter
from time import time
from psutil import NoSuchProcess, Process
import yaml
from pytz import UTC
from texttable import Texttable
from zato.common.api import INFO_FORMAT, MISC, ZATO_INFO_FILE
from zato.common.json_internal import dumps as json_dumps, loads as json_loads
from zato.common.util.api import current_host
from zato.common.util.open_ import open_r
from zato.common.typing_ import stranydict


def format_connections(conns: Any, format: Any) -> None: ...

def get_worker_pids(component_path: Any) -> None: ...

def get_info(component_path: Any, format: Any, _now: Any = ...) -> stranydict: ...

def format_info(value: Any, format: Any, cols_width: Any = ..., dumper: Any = ...) -> None: ...
