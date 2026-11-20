# dialects/sqlite/__init__.py
# Copyright (C) 2005-2026 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors


from importlib import import_module

from . import base  # noqa
from . import pysqlite  # noqa
from .base import BLOB
from .base import BOOLEAN
from .base import CHAR
from .base import DATE
from .base import DATETIME
from .base import DECIMAL
from .base import FLOAT
from .base import INTEGER
from .base import JSON
from .base import JSONB
from .base import NUMERIC
from .base import REAL
from .base import SMALLINT
from .base import TEXT
from .base import TIME
from .base import TIMESTAMP
from .base import VARCHAR
from .dml import Insert
from .dml import insert

# default dialect
base.dialect = dialect = pysqlite.dialect

# Zato - the dialects of the drivers that no engine of Zato uses are imported
# on the first access to them, e.g. when the registry of dialects loads one.
_lazy_dialects = ("aiosqlite", "pysqlcipher")


def __getattr__(name):
    if name not in _lazy_dialects:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return import_module(f"{__name__}.{name}")


__all__ = (
    "BLOB",
    "BOOLEAN",
    "CHAR",
    "DATE",
    "DATETIME",
    "DECIMAL",
    "FLOAT",
    "INTEGER",
    "JSON",
    "JSONB",
    "NUMERIC",
    "SMALLINT",
    "TEXT",
    "TIME",
    "TIMESTAMP",
    "VARCHAR",
    "REAL",
    "Insert",
    "insert",
    "dialect",
)
