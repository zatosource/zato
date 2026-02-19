from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
import os
from logging import getLogger
from sqlalchemy import Column, create_engine, Integer, Sequence, String, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

class Setting(Base):
    __tablename__: Any
    __table_args__: Any
    id: Any
    name: Any
    value: Any
    data_type: Any

class DATA_TYPE:
    INTEGER: Any
    STRING: Any

class SettingsDB:
    def __init__(self: Any, db_path: Any, session: Any) -> None: ...
    def get_engine(self: Any) -> None: ...
    def create_db(self: Any) -> None: ...
    def get(self: Any, name: Any, default: Any = ..., needs_object: Any = ...) -> None: ...
    def set(self: Any, name: Any, value: Any, data_type: Any = ...) -> None: ...
