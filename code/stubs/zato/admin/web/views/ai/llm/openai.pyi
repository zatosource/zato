from typing import Any, TYPE_CHECKING

import json
from logging import getLogger
from urllib.request import Request, urlopen
from zato.admin.web.views.ai.browser_tools import is_browser_tool
from zato.admin.web.views.ai.llm.base import BaseLLMClient, Max_Tool_Iterations
from zato.admin.web.views.ai.llm.execution import ExecutionLog
from zato.common.typing_ import anylist, generator_


class OpenAIClient(BaseLLMClient):
    def stream_chat(self: Any, model: str, messages: list) -> generator_: ...
    def _convert_tools_to_openai_format(self: Any, tools: anylist) -> anylist: ...
    def _execute_tools_batched(self: Any, tool_calls: list, all_tools: anylist, execution_log: ExecutionLog) -> list: ...
    def _stream_single_request(self: Any, model: str, messages: list, tools: anylist) -> generator_: ...
