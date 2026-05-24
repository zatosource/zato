# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from contextvars import ContextVar

# ################################################################################################################################
# ################################################################################################################################

current_cid: ContextVar[str] = ContextVar('current_cid', default='')
current_service_name: ContextVar[str] = ContextVar('current_service_name', default='')

# ################################################################################################################################
# ################################################################################################################################

class ServiceContextFilter(logging.Filter):
    def filter(self, record):
        _cid = current_cid.get()
        _service_name = current_service_name.get()
        if _cid:
            record.zato_ctx = ' ' + _service_name + ' - ' + _cid + ' -'
        else:
            record.zato_ctx = ''
        return True

# ################################################################################################################################
# ################################################################################################################################

logging_conf_contents = """
loggers:
    '':
        level: INFO
        handlers: [stdout, default]
    'zato.server.main':
        level: INFO
        handlers: [stdout, default]
    'pytds':
        level: WARN
        handlers: [stdout, default]
    zato:
        level: INFO
        handlers: [stdout, default]
        qualname: zato
        propagate: false
    zato_rest:
        level: INFO
        handlers: [stdout, default]
        qualname: zato
        propagate: false
    zato_access_log:
        level: INFO
        handlers: [http_access_log]
        qualname: zato_access_log
        propagate: false
    zato_admin:
        level: INFO
        handlers: [admin]
        qualname: zato_admin
        propagate: false
    zato_audit_pii:
        level: INFO
        handlers: [stdout, audit_pii]
        qualname: zato_audit_pii
        propagate: false
    zato_connector:
        level: INFO
        handlers: [connector]
        qualname: zato_connector
        propagate: false
    zato_scheduler:
        level: INFO
        handlers: [stdout, scheduler]
        qualname: zato_scheduler
        propagate: false
handlers:
    default:
        formatter: default
        class: {log_handler_class}
        filename: './logs/server.log'
        mode: 'a'
        maxBytes: {server_log_max_size}
        backupCount: {server_log_backup_count}
        encoding: 'utf8'
    stdout:
        formatter: default
        class: logging.StreamHandler
        stream: ext://sys.stdout
    http_access_log:
        formatter: default
        class: {log_handler_class}
        filename: './logs/http_access.log'
        mode: 'a'
        maxBytes: {server_log_max_size}
        backupCount: {server_log_backup_count}
        encoding: 'utf8'
    admin:
        formatter: default
        class: {log_handler_class}
        filename: './logs/admin.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
        encoding: 'utf8'
    audit_pii:
        formatter: default
        class: logging.handlers.RotatingFileHandler
        filename: './logs/audit-pii.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
        encoding: 'utf8'
    connector:
        formatter: default
        class: {log_handler_class}
        filename: './logs/connector.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
        encoding: 'utf8'
    scheduler:
        formatter: default
        class: {log_handler_class}
        filename: './logs/scheduler.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
        encoding: 'utf8'

formatters:
    audit_pii:
        format: '%(message)s'
    default:
        format: '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s -%(zato_ctx)s %(name)s:%(lineno)d - %(message)s'
    http_access_log:
        format: '%(remote_ip)s %(cid_resp_time)s "%(channel_name)s" [%(req_timestamp)s] "%(method)s %(path)s %(http_version)s" %(status_code)s %(response_size)s "-" "%(user_agent)s"'
version: 1
""" # noqa: E501

# ################################################################################################################################
# ################################################################################################################################

def get_logging_conf_contents() -> 'str':
    # type: (str) -> str

    # We import it here to make CLI work faster
    from zato.common.util.platform_ import is_linux

    linux_log_handler_class     = 'logging.handlers.RotatingFileHandler' # Previously = ConcurrentRotatingFileHandler
    non_linux_log_handler_class = 'logging.handlers.RotatingFileHandler'

    # Under Windows, we cannot have multiple processes access the same log file
    log_handler_class = linux_log_handler_class if is_linux else non_linux_log_handler_class

    # This can be overridden by users
    if server_log_max_size := os.environ.get('Zato_Server_Log_Max_Size'):
        server_log_max_size = int(server_log_max_size)
    else:
        server_log_max_size = 1000000000 # 1 GB by default

    # This can be overridden by users
    if server_log_backup_count := os.environ.get('Zato_Server_Log_Backup_Count'):
        server_log_backup_count = int(server_log_backup_count)
    else:
        server_log_backup_count = 2

    return logging_conf_contents.format(
        log_handler_class=log_handler_class,
        server_log_max_size=server_log_max_size,
        server_log_backup_count=server_log_backup_count,
    )

# ################################################################################################################################
# ################################################################################################################################
