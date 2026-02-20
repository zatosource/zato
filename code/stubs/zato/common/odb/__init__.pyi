from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
import copy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from zato.common.util.api import get_engine_url
import logging
from traceback import format_exc
from sqlalchemy.sql import text
import pymysql
import pg8000


def ping_database(params: Any, ping_query: Any) -> None: ...

def create_pool(engine_params: Any, ping_query: Any, query_class: Any = ...) -> None: ...

def drop_all(engine: Any) -> None: ...
