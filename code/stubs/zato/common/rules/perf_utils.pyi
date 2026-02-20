from typing import Any, TYPE_CHECKING

import os
import time
import signal
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean, median, stdev
from zato.common.rules.api import RulesManager
from colorama import Fore, Style, init
import tempfile


class ASCIITable:
    @staticmethod
    def make_table(data: Any, headers: Any) -> None: ...

class BarChart:
    @staticmethod
    def render(data: Any, title: Any = ..., xlabel: Any = ..., ylabel: Any = ..., width: Any = ..., height: Any = ...) -> None: ...

class RulePerformanceTester:
    rules_dir: Any
    pattern: Any
    results: Any
    rule_groups: Any
    group_times: Any
    total_start_time: time.time
    interrupted: Any
    perf_dir: Any
    rule_files: sorted
    test_data: self._generate_test_data
    def __init__(self: Any, rules_dir: Any = ..., pattern: Any = ...) -> None: ...
    def _find_rule_files(self: Any) -> None: ...
    def _generate_test_data(self: Any) -> None: ...
    def _setup_signal_handler(self: Any) -> None: ...
    def test_file(self: Any, file_path: Any, iterations: Any = ..., runs_per_iteration: Any = ...) -> None: ...
    def filter_by_rule_counts(self: Any, rule_counts: Any) -> None: ...
    def run_tests(self: Any, iterations: Any = ..., runs_per_iteration: Any = ...) -> None: ...
    def _display_group_results(self: Any, rule_count: Any) -> None: ...
    def display_results(self: Any) -> None: ...
    def _save_plain_text_summary(self: Any, sorted_results: Any, total_time: Any) -> None: ...
