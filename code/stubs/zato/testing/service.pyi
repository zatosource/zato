from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals

class TestingService:
    schema: Any
    @staticmethod
    def after_add_to_store(*ignored_args: Any, **ignored_kwargs: Any) -> None: ...
