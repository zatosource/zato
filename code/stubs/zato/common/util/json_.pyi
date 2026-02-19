from typing import Any

from simdjson import Parser as SIMDJSONParser
from simdjson import loads as json_loads
from json import loads as json_loads

class BasicParser:
    def parse(self: Any, value: Any) -> None: ...
