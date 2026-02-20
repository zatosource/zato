from typing import Any, TYPE_CHECKING

import json
from logging import getLogger
from traceback import format_exc
from urllib.request import Request, urlopen
from zato.admin.web.views.ai.browser_tools import is_browser_tool
from zato.admin.web.views.ai.llm.base import BaseLLMClient, Max_Tool_Iterations
from zato.admin.web.views.ai.llm.execution import ExecutionLog
from zato.admin.web.views.ai.llm.guidance import select_guidance_for_message
from zato.common.typing_ import anylist, generator_


class AnthropicClient(BaseLLMClient):
    def stream_chat(self: Any, model: str, messages: list) -> generator_: ...
    def _extract_response_text(self: Any, assistant_content: list) -> str: ...
    def _convert_tools_to_anthropic_format(self: Any, mcp_tools: anylist) -> anylist: ...
    def _execute_tools_batched(self: Any, tool_calls: list, all_tools: anylist, execution_log: ExecutionLog) -> list: ...
    def _stream_single_request(self: Any, model: str, messages: list, tools: anylist) -> generator_: ...
