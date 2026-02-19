from typing import Any

from logging import getLogger
from django.http import JsonResponse
from zato.admin.web.views import method_allowed
from zato.admin.web.views.ai.mcp.registry import MCPRegistry
from zato.common.json_internal import loads
from django.http import HttpRequest

def get_servers(req: HttpRequest) -> JsonResponse: ...

def add_server(req: HttpRequest) -> JsonResponse: ...

def remove_server(req: HttpRequest) -> JsonResponse: ...

def update_server(req: HttpRequest) -> JsonResponse: ...

def get_tools(req: HttpRequest) -> JsonResponse: ...

def invoke_tool(req: HttpRequest) -> JsonResponse: ...
