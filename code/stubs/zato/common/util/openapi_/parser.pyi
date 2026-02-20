from typing import Any, TYPE_CHECKING

import argparse
import json
import os
import traceback
from dataclasses import asdict, dataclass
import requests
import yaml


class OpenAPIPathItem:
    name: str
    path: str
    auth: str
    auth_server_url: str
    content_type: str

class OpenAPIDefinition:
    servers: list[str]
    paths: list[OpenAPIPathItem]

class Parser:
    def from_data(self: Any, data: str) -> OpenAPIDefinition: ...
    def from_url(self: Any, url: str) -> OpenAPIDefinition: ...

def _print_definition(name: str, definition: OpenAPIDefinition) -> None: ...

def _run_demo() -> None: ...
