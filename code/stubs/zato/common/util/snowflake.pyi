from typing import Any

import _thread
import os
import platform
import random
from zato.common.util.time_ import utcnow
from zato.common.typing_ import anydict

class SnowflakeGenerator:
    def __init__(self: Any, machine_id: str) -> None: ...
    def generate_id(self: Any, suffix: str) -> str: ...

def create_snowflake_generator(machine_id: str = ...) -> SnowflakeGenerator: ...

def new_snowflake(suffix: str, needs_machine_id: bool = ...) -> str: ...
