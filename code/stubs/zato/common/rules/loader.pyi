from typing import Any, TYPE_CHECKING

from logging import getLogger
from pathlib import Path
from threading import RLock
from zato.common.rules.models import Container, Rule
from zato.common.rules.parser import parse_file
from zato.common.typing_ import any_, dict_, str, strdict, strlist
from zato.common.rules.cache import CachedRule
from rule_engine import Rule as RuleImpl


class RuleLoader:
    _lock: RLock
    def __init__(self: Any) -> None: ...
    def load_parsed_rules(self: Any, parsed: strdict, container_name: str, all_rules: dict_[str, Rule], containers: dict_[str, Container], cached_rules: dict_[str, any_]) -> strlist: ...
    def load_rules_from_file(self: Any, file_path: str | Path, all_rules: dict_[str, Rule], containers: dict_[str, Container], cached_rules: dict_[str, any_]) -> strlist: ...
    def load_rules_from_directory(self: Any, root_dir: str | Path, all_rules: dict_[str, Rule], containers: dict_[str, Container], cached_rules: dict_[str, any_]) -> strlist: ...
