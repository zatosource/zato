from typing import Any

from logging import DEBUG, getLogger
from sqlalchemy.exc import InternalError as SAInternalError, OperationalError as SAOperationalError
from zato.common.typing_ import any_, callable_

def sql_op_with_deadlock_retry(cid: Any, name: Any, func: Any, *args: Any, **kwargs: Any) -> any_: ...

def sql_query_with_retry(query: any_, query_name: str, *args: any_) -> None: ...
