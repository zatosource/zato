from typing import Any, TYPE_CHECKING

import argparse
import copy
import logging
import os
import yaml
from zato.common.typing_ import strdict


class EnmasseGenerator:
    current_dir: os.path.dirname
    server_config_dir: os.path.join
    config_path: os.path.abspath
    multi_config_path: os.path.abspath
    def __init__(self: Any) -> None: ...
    def _add_users_topics_and_subscriptions(self: Any, config_data: strdict, users: int, topics_multiplier: float) -> strdict: ...
    def load_config(self: Any) -> strdict: ...
    def create_multi_config(self: Any, modified_config: strdict) -> None: ...
    def log_config_info(self: Any, config_data: strdict, users: int) -> None: ...
    def generate(self: Any, users: int, topics_multiplier: float) -> None: ...
