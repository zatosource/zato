from typing import Any, TYPE_CHECKING

import base64
import json
import logging
import os
import time
from http.client import HTTPSConnection

user_id = os.environ[Any]
api_key = os.environ[Any]
host = os.environ[Any]

def push_milestone(process_id: Any, milestone_name: Any) -> None: ...
