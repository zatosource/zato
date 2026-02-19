from typing import Any

import ast
import os
import re
from logging import getLogger
from bunch import bunchify
import rule_engine
from zato.common.util.api import as_bool
from zato.common.util.open_ import open_r
from zato.common.util.sorted_dict import SortedDict
from pathlib import Path
from zato.common.typing_ import any_, strdict
import json
import sys

def parse_file(path: str | Path, container_name: str) -> strdict: ...

def parse_assignments(text: str) -> any_: ...

def parse_data(data: str, container_name: str) -> strdict: ...

def remove_comments(text: str) -> str: ...
