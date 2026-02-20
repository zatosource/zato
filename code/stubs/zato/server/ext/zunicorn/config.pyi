from typing import Any

import copy
import inspect
import os
import re
import ssl
import sys
import textwrap
import shlex
from zato.common.util.platform_ import is_posix
from zato.server.ext.zunicorn import _compat
from zato.server.ext.zunicorn.errors import ConfigError
from zato.server.ext.zunicorn.reloader import reloader_engines
from zato.server.ext.zunicorn import six
from zato.server.ext.zunicorn import util
import argparse
import pwd
import grp
from zato.server.ext.zunicorn import SERVER_SOFTWARE

def make_settings(ignore: Any = ...) -> None: ...

def auto_int(_: Any, x: Any) -> None: ...

class Config:
    settings: make_settings
    usage: Any
    prog: Any
    env_orig: os.environ.copy
    server_software: Any
    def __init__(self: Any, usage: Any = ..., prog: Any = ...) -> None: ...
    def __getattr__(self: Any, name: Any) -> None: ...
    def __setattr__(self: Any, name: Any, value: Any) -> None: ...
    def set(self: Any, name: Any, value: Any) -> None: ...
    def get_cmd_args_from_env(self: Any) -> None: ...
    def parser(self: Any) -> None: ...
    @property
    def worker_class_str(self: Any) -> None: ...
    @property
    def worker_class(self: Any) -> None: ...
    @property
    def address(self: Any) -> None: ...
    @property
    def uid(self: Any) -> None: ...
    @property
    def gid(self: Any) -> None: ...
    @property
    def proc_name(self: Any) -> None: ...
    @property
    def logger_class(self: Any) -> None: ...
    @property
    def is_ssl(self: Any) -> None: ...
    @property
    def ssl_options(self: Any) -> None: ...
    @property
    def env(self: Any) -> None: ...
    @property
    def sendfile(self: Any) -> None: ...
    @property
    def reuse_port(self: Any) -> None: ...
    @property
    def paste_global_conf(self: Any) -> None: ...

class SettingMeta(type):
    def __new__(cls: Any, name: Any, bases: Any, attrs: Any) -> None: ...
    def fmt_desc(cls: Any, desc: Any) -> None: ...

class Setting:
    name: Any
    value: Any
    section: Any
    cli: Any
    validator: Any
    type: Any
    meta: Any
    action: Any
    default: Any
    short: Any
    desc: Any
    nargs: Any
    const: Any
    __cmp__: Any
    def __init__(self: Any) -> None: ...
    def add_option(self: Any, parser: Any) -> None: ...
    def copy(self: Any) -> None: ...
    def get(self: Any) -> None: ...
    def set(self: Any, val: Any) -> None: ...
    def __lt__(self: Any, other: Any) -> None: ...

def validate_bool(val: Any) -> None: ...

def validate_dict(val: Any) -> None: ...

def validate_pos_int(val: Any) -> None: ...

def validate_string(val: Any) -> None: ...

def validate_file_exists(val: Any) -> None: ...

def validate_list_string(val: Any) -> None: ...

def validate_list_of_existing_files(val: Any) -> None: ...

def validate_string_to_list(val: Any) -> None: ...

def validate_class(val: Any) -> None: ...

def validate_callable(arity: Any) -> None: ...

def validate_user(val: Any) -> None: ...

def validate_group(val: Any) -> None: ...

def validate_post_request(val: Any) -> None: ...

def validate_chdir(val: Any) -> None: ...

def validate_hostport(val: Any) -> None: ...

def validate_reload_engine(val: Any) -> None: ...

def get_default_config_file() -> None: ...

class ConfigFile(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class Bind(Setting):
    name: Any
    action: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    desc: Any

class Backlog(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class Workers(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class WorkerClass(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class WorkerThreads(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class WorkerConnections(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class MaxRequests(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class MaxRequestsJitter(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class Timeout(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class GracefulTimeout(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class Keepalive(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class LimitRequestLine(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class LimitRequestFields(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class LimitRequestFieldSize(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class Reload(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class ReloadEngine(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class ReloadExtraFiles(Setting):
    name: Any
    action: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class Spew(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class ConfigCheck(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class PreloadApp(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class Sendfile(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    const: Any
    desc: Any

class ReusePort(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class Chdir(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    default: Any
    desc: Any

class Daemon(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class Env(Setting):
    name: Any
    action: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class Pidfile(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class WorkerTmpDir(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class User(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    desc: Any

class Group(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    desc: Any

class Umask(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    type: Any
    default: Any
    desc: Any

class Initgroups(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class TmpUploadDir(Setting):
    name: Any
    section: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class SecureSchemeHeader(Setting):
    name: Any
    section: Any
    validator: Any
    default: Any
    desc: Any

class ForwardedAllowIPS(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class AccessLog(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class DisableRedirectAccessToSyslog(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class AccessLogFormat(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class ErrorLog(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class Loglevel(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class CaptureOutput(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class LoggerClass(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class LogConfig(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class LogConfigDict(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    default: Any
    desc: Any

class SyslogTo(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    desc: Any

class Syslog(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class SyslogPrefix(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class SyslogFacility(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class EnableStdioInheritance(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    default: Any
    action: Any
    desc: Any

class StatsdHost(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    default: Any
    validator: Any
    desc: Any

class StatsdPrefix(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    default: Any
    validator: Any
    desc: Any

class Procname(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class DefaultProcName(Setting):
    name: Any
    section: Any
    validator: Any
    default: Any
    desc: Any

class PythonPath(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class Paste(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class OnStarting(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def on_starting(server: Any) -> None: ...

class OnReload(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def on_reload(server: Any) -> None: ...

class WhenReady(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def when_ready(server: Any) -> None: ...

class Prefork(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def pre_fork(server: Any, worker: Any) -> None: ...

class Postfork(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def post_fork(server: Any, worker: Any) -> None: ...

class PostWorkerInit(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def post_worker_init(worker: Any) -> None: ...

class WorkerInt(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def worker_int(worker: Any) -> None: ...

class WorkerAbort(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def worker_abort(worker: Any) -> None: ...

class PreExec(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def pre_exec(server: Any) -> None: ...

class PreRequest(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def pre_request(worker: Any, req: Any) -> None: ...

class PostRequest(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def post_request(worker: Any, req: Any, environ: Any, resp: Any) -> None: ...

class ChildExit(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def child_exit(server: Any, worker: Any) -> None: ...

class WorkerExit(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def worker_exit(server: Any, worker: Any) -> None: ...

class BeforePidKill(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def before_pid_kill(server: Any, worker: Any) -> None: ...

class NumWorkersChanged(Setting):
    name: Any
    section: Any
    validator: Any
    type: Any
    default: Any
    desc: Any
    def nworkers_changed(server: Any, new_value: Any, old_value: Any) -> None: ...

class OnExit(Setting):
    name: Any
    section: Any
    validator: Any
    default: Any
    desc: Any
    def on_exit(server: Any) -> None: ...

class ProxyProtocol(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    default: Any
    action: Any
    desc: Any

class ProxyAllowFrom(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    default: Any
    desc: Any

class KeyFile(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class CertFile(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class SSLVersion(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    default: Any
    desc: Any

class CertReqs(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    default: Any
    desc: Any

class CACerts(Setting):
    name: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any

class SuppressRaggedEOFs(Setting):
    name: Any
    section: Any
    cli: Any
    action: Any
    default: Any
    validator: Any
    desc: Any

class DoHandshakeOnConnect(Setting):
    name: Any
    section: Any
    cli: Any
    validator: Any
    action: Any
    default: Any
    desc: Any

class PasteGlobalConf(Setting):
    name: Any
    action: Any
    section: Any
    cli: Any
    meta: Any
    validator: Any
    default: Any
    desc: Any
