from typing import Any, TYPE_CHECKING

from zato.admin.web.views.ai.llm.anthropic import AnthropicClient
from zato.admin.web.views.ai.llm.base import BaseLLMClient
from zato.admin.web.views.ai.llm.google import GoogleClient
from zato.admin.web.views.ai.llm.openai import OpenAIClient


def get_llm_client(provider: str, api_key: str, zato_client: any_ = ..., cluster_id: int = ..., cluster: any_ = ..., session_id: str = ...) -> BaseLLMClient: ...
