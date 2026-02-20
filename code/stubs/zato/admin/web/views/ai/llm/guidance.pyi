from typing import Any, TYPE_CHECKING

from logging import getLogger
from operator import itemgetter
from fastembed import TextEmbedding
from zato.common.typing_ import anylist


class GuidanceSelector:
    model: Any
    guidance_vectors: Any
    _initialized: Any
    def __init__(self: Any) -> None: ...
    def _ensure_initialized(self: Any) -> None: ...
    def select_guidance(self: Any, user_message: str, top_k: int = ..., threshold: float = ...) -> anylist: ...

def get_guidance_selector() -> GuidanceSelector: ...

def select_guidance_for_message(user_message: str, top_k: int = ...) -> str: ...
