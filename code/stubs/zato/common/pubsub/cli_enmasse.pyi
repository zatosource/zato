from typing import Any

import argparse
import logging
import os
import sys
import tempfile
from logging import basicConfig, getLogger, INFO
from traceback import format_exc
from zato.common.test.enmasse_.base import BaseEnmasseTestCase

class EnmasseCLI(BaseEnmasseTestCase):
    def run_enmasse_import(self: Any, yaml_content: str) -> bool: ...

def get_parser() -> argparse.ArgumentParser: ...

def run_enmasse_command(args: argparse.Namespace) -> int: ...

def main() -> int: ...
