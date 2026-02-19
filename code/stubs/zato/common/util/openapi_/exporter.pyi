from typing import Any

import logging
from traceback import format_exc
from zato.openapi.generator.io_scanner import IOScanner
from zato.openapi.generator.openapi_ import OpenAPIGenerator
import yaml

def build_openapi_spec(channel_name: Any, services_info: Any, file_paths: Any) -> None: ...
