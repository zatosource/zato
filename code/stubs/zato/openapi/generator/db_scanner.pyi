from typing import Any

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zato.common.odb.model import HTTPBasicAuth, APIKeySecurity, HTTPSOAP, GenericObject

def fetch_all() -> None: ...

def build_scan_results() -> None: ...
