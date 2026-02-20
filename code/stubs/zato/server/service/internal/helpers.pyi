from typing import Any, TYPE_CHECKING

import os
from contextlib import closing
from dataclasses import dataclass
from io import StringIO
from json import loads
from logging import DEBUG, getLogger
from tempfile import gettempdir
from traceback import format_exc
from unittest import TestCase
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from zato.common.test import rand_csv, rand_string
from zato.common.typing_ import cast_, intnone, list_, optional
from zato.common.util.api import utcnow
from zato.common.util.open_ import open_w
from zato.server.commands import CommandResult, Config
from zato.common.api import CONNECTION, GENERIC, SEC_DEF_TYPE, URL_TYPE
from zato.common.util.auth import check_basic_auth
from zato.server.connection.http_soap import Forbidden, Unauthorized
from zato.server.service import Model, Service
from zato.common.typing_ import any_, anydict
import logging
import django
from django.conf import settings
from django.template import Context, Template
from zato.common.odb.model import SecurityBase
from zato.common.odb.model import GenericConn, HTTPSOAP
from zato.common.util.openapi_.exporter import build_openapi_spec
from zato.server.connection.http_soap import BadRequest
from zato.server.service.internal.helpers import PubInputLogger


class User(Model):
    user_id: int
    username: str
    display_name: optional[str]

class UserAccount(Model):
    user: User
    account_id: int
    account_type: intnone

class GetUserRequest(Model):
    username: str

class GetUserAccountListRequest(Model):
    user_id: optional[int]
    account_id: int

class GetUserAccountListResponse(Model):
    user_account_list: list_[UserAccount]

class GetUserResponse(Model):
    user: list_[User]
    parent_user: list_[optional[User]]
    previous_user: optional[list_[User]]

class ToggleLogStreaming(Service):
    name: Any
    def handle(self: Any) -> None: ...

class GetLogStreamingStatus(Service):
    name: Any
    def handle(self: Any) -> None: ...

class Echo(Service):
    name: Any
    def handle(self: Any) -> None: ...

class PubInputLogger(Service):
    name: Any
    input: Any
    output: Any
    def handle(self: Any) -> None: ...

class GetMetrics(Service):
    name: Any
    def handle(self: Any) -> None: ...

class HTMLService(Service):
    def before_handle(self: Any) -> None: ...
    def set_html_payload(self: Any, ctx: any_, template: str, content_type: str = ...) -> None: ...

class BaseServiceGateway:
    def _check_service_allowed(self: Any, service: Any, channel_id: Any) -> None: ...
    def _set_sec_def(self: Any, username: Any) -> None: ...
    def _invoke_service(self: Any, service: Any, request: Any) -> None: ...

class ServiceGateway(BaseServiceGateway, Service):
    name: Any
    def handle(self: Any) -> None: ...

class DjangoServiceGateway(BaseServiceGateway, Service):
    name: Any
    username: Any
    def handle(self: Any) -> None: ...

class APISpecHelperUser(Service):
    name: Any
    def handle(self: Any) -> None: ...

class MyUser(Model):
    user_name: str
    address_data: dict
    prefs_dict: optional[dict]
    phone_list: list
    email_list: optional[list]

class MyAccount(Model):
    account_no: int
    account_type: str
    account_segment: str

class MyAccountList(Model):
    account_list: list_[MyAccount]

class MyRequest(Model):
    request_id: int
    user: MyUser

class MyResponse(Model):
    current_balance: int
    last_account_no: int
    pref_account: MyAccount
    account_list: MyAccountList

class MyDataclassService(Service):
    name: Any
    def handle(self: Any) -> None: ...

class CommandsService(Service):
    name: Any
    def handle(self: Any) -> None: ...

class OpenAPIHandler(Service):
    name: Any
    def _get_active_rest_channel_ids(self: Any, channel: Any) -> None: ...
    def _get_basic_auth_security_ids(self: Any, session: Any, rest_channels: Any) -> None: ...
    def _check_credentials(self: Any, auth_header: Any, basic_auth_security_ids: Any) -> None: ...
    def _collect_services_info(self: Any, rest_channels: Any) -> None: ...
    def handle(self: Any) -> None: ...
