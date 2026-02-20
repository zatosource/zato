from typing import Any, TYPE_CHECKING

import argparse
import sys
from json import dumps
from logging import basicConfig, getLogger
from zato.common.pubsub.test.message_sender import MessageSender
from zato.common.util.api import get_absolute_path


def parse_args() -> None: ...

def main() -> None: ...
