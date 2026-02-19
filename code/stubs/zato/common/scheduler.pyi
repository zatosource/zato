from typing import Any

from dataclasses import dataclass
from zato.common.typing_ import list_, strdict, strlist
from zato.common.util.api import get_config_from_string

class SchedulerCredentials:
    username: str
    password: str

class PathAction:
    path: str
    action: str

class _BaseConfig:
    host: str
    port: int
    use_tls: bool
    verify_tls: bool

class ServerSchedulerConfig(_BaseConfig):
    username: str
    password: str

class SchedulerConfig(_BaseConfig):
    bind_host: str
    bind_port: int
    tls_version: str
    tls_version: str
    tls_ciphers: str
    priv_key_location: str
    pub_key_location: str
    cert_location: str
    ca_certs_location: str
    api_user_list: list_[SchedulerCredentials]
    config_action_user_list: list_[SchedulerCredentials]

def get_startup_job_services() -> strlist: ...

def get_server_scheduler_config(fs_config: strdict) -> ServerSchedulerConfig: ...
