from typing import Any

import json
import re
from datetime import datetime
from enum import Enum
from logging import getLogger
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from zato.admin.web.views.ai.common import get_redis_client
from zato.common.typing_ import anydict

class QueryIntent(Enum):
    Current_State: Any
    Event_History: Any
    Ambiguous: Any

def detect_intent(question: str) -> QueryIntent: ...

class ToolRecord(BaseModel):
    tool_name: str
    model_name: str
    object_id: str
    object_name: str
    action: str
    arguments: Dict[str, Any]
    result: Optional[Any]
    success: bool
    error: Optional[str]
    old_content: str
    new_content: str
    is_new: bool

class ExecutionLog(BaseModel):
    records: List[ToolRecord]
    def add(self: Any, tool_name: str, arguments: dict, result: Any = ..., success: bool = ..., error: str = ...) -> None: ...
    def clear(self: Any) -> None: ...
    def build_ground_truth_message(self: Any) -> str: ...
    def get_object_changes(self: Any) -> List[Dict[str, Any]]: ...
    def _format_object_type(self: Any, model_name: str) -> str: ...
    def verify_response(self: Any, response_text: str) -> List[str]: ...
    def build_deterministic_response(self: Any) -> str: ...
    def persist(self: Any, session_id: str, conversation_turn: int = ...) -> None: ...

def get_state_snapshot(session_id: str, model_name: str = ...) -> dict: ...

def get_event_log(session_id: str, count: int = ...) -> list: ...

def build_state_context(session_id: str) -> str: ...

def build_history_context(session_id: str, count: int = ...) -> str: ...

def build_execution_context(session_id: str, question: str = ...) -> str: ...

def clear_session_state(session_id: str) -> None: ...
