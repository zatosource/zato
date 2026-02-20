from typing import Any, TYPE_CHECKING

import os
import warnings
from zato.common.ext.dictalchemy import make_class_dictable
from sqlalchemy import Text, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from zato.common.json_internal import json_dumps, json_loads
from zato.common.typing_ import any_


class _JSON(TypeDecorator):
    cache_ok: Any
    impl: Any
    @property
    def python_type(self: Any) -> None: ...
    def process_bind_param(self: Any, value: Any, dialect: Any) -> None: ...
    def process_literal_param(self: Any, value: Any, dialect: Any) -> None: ...
    def process_result_value(self: Any, value: Any, dialect: Any) -> None: ...
