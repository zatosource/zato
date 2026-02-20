from typing import Any, TYPE_CHECKING

import os
from zato.server.ext.zunicorn.errors import ConfigError
from zato.server.ext.zunicorn.app.base import Application
from zato.server.ext.zunicorn import util
from zato.server.ext.zunicorn.app.wsgiapp import WSGIApplication
from pasterapp import load_pasteapp
from pasterapp import paste_config


class WSGIApplication(Application):
    def init(self: Any, parser: Any, opts: Any, args: Any) -> None: ...
    def load_wsgiapp(self: Any) -> None: ...
    def load_pasteapp(self: Any) -> None: ...
    def load(self: Any) -> None: ...

def run() -> None: ...
