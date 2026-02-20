from typing import Any, TYPE_CHECKING

from pathlib import Path

_prompts_dir = Path.resolve.parent

def get_system_prompt() -> str: ...
