from typing import Any

from typing import Callable
from zato.common.util.api import make_repr

class SearchResults:
    q: Any
    result: Any
    total: Any
    columns: Any
    num_pages: Any
    cur_page: Any
    prev_page: Any
    next_page: Any
    has_prev_page: Any
    has_next_page: Any
    page_size: Any
    def __init__(self: Any, q: Any, result: Any, columns: Any, total: Any) -> None: ...
    def __iter__(self: Any) -> None: ...
    def __repr__(self: Any) -> None: ...
    def set_data(self: Any, cur_page: Any, page_size: Any) -> None: ...
    @staticmethod
    def from_list(data_list: Any, cur_page: Any, page_size: Any, needs_sort: Any = ..., post_process_func: Any = ..., sort_key: Any = ..., needs_reverse: Any = ...) -> None: ...
    def to_dict(self: Any, _search_attrs: Any = ...) -> None: ...
