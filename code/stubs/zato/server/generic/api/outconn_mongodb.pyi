from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from logging import getLogger
from uuid import uuid4
from bunch import bunchify
from pymongo import MongoClient
from zato.server.connection.wrapper import Wrapper

class OutconnMongoDBWrapper(Wrapper):
    wrapper_type: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def _init_impl(self: Any) -> None: ...
    def _delete(self: Any) -> None: ...
    def _ping(self: Any) -> None: ...
