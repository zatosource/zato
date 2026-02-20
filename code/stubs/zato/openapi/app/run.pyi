from typing import Any, TYPE_CHECKING

import logging
import os
import sys
import gunicorn.app.base
from zato.openapi.app.wsgi import application


class OpenAPIServer(gunicorn.app.base.BaseApplication):
    options: Any
    application: Any
    def __init__(self: Any, app: Any, options: Any = ...) -> None: ...
    def load_config(self: Any) -> None: ...
    def load(self: Any) -> None: ...

def main() -> None: ...
