# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import Formatter

# ################################################################################################################################
# ################################################################################################################################

logging_conf_contents = """
loggers:
    '':
        level: INFO
        handlers: [stdout, default]
    'gunicorn.main':
        level: INFO
        handlers: [stdout, default]
    zato:
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
    zato_hl7:
        level: INFO
        handlers: [stdout, hl7]
        qualname: zato_hl7
        propagate: false
    zato_kvdb:
        level: INFO
        handlers: [kvdb]
        qualname: zato_kvdb
        propagate: false
    zato_pubsub:
        level: INFO
        handlers: [stdout, pubsub]
        qualname: zato_pubsub
        propagate: false
    zato_pubsub_overflow:
        level: INFO
        handlers: [pubsub_overflow]
        qualname: zato_pubsub_overflow
        propagate: false
    zato_pubsub_audit:
        level: INFO
        handlers: [pubsub_audit]
        qualname: zato_pubsub_audit
        propagate: false
    zato_rbac:
        level: INFO
        handlers: [rbac]
        qualname: zato_rbac
        propagate: false
    zato_scheduler:
        level: INFO
        handlers: [stdout, scheduler]
        qualname: zato_scheduler
        propagate: false
    zato_web_socket:
        level: INFO
        handlers: [stdout, web_socket]
        qualname: zato_web_socket
        propagate: false
    zato_ibm_mq:
        level: INFO
        handlers: [stdout, ibm_mq]
        qualname: zato_ibm_mq
        propagate: false
    zato_notif_sql:
        level: INFO
        handlers: [stdout, notif_sql]
        qualname: zato_notif_sql
        propagate: false
handlers:
    default:
        formatter: default
        class: {log_handler_class}
        filename: './logs/server.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    stdout:
        formatter: colour
        class: logging.StreamHandler
        stream: ext://sys.stdout
    http_access_log:
        formatter: http_access_log
        class: {log_handler_class}
        filename: './logs/http_access.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    admin:
        formatter: default
        class: {log_handler_class}
        filename: './logs/admin.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    audit_pii:
        formatter: default
        class: logging.handlers.RotatingFileHandler
        filename: './logs/audit-pii.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    connector:
        formatter: default
        class: {log_handler_class}
        filename: './logs/connector.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    hl7:
        formatter: default
        class: {log_handler_class}
        filename: './logs/hl7.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    kvdb:
        formatter: default
        class: {log_handler_class}
        filename: './logs/kvdb.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    pubsub:
        formatter: default
        class: {log_handler_class}
        filename: './logs/pubsub.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    pubsub_overflow:
        formatter: default
        class: {log_handler_class}
        filename: './logs/pubsub-overflow.log'
        mode: 'a'
        maxBytes: 200000000
        backupCount: 50
    pubsub_audit:
        formatter: default
        class: {log_handler_class}
        filename: './logs/pubsub-audit.log'
        mode: 'a'
        maxBytes: 200000000
        backupCount: 50
    rbac:
        formatter: default
        class: {log_handler_class}
        filename: './logs/rbac.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    scheduler:
        formatter: default
        class: {log_handler_class}
        filename: './logs/scheduler.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    web_socket:
        formatter: default
        class: {log_handler_class}
        filename: './logs/web_socket.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    ibm_mq:
        formatter: default
        class: logging.handlers.RotatingFileHandler
        filename: './logs/ibm-mq.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
    notif_sql:
        formatter: default
        class: logging.handlers.RotatingFileHandler
        filename: './logs/notif-sql.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10

formatters:
    audit_pii:
        format: '%(message)s'
    default:
        format: '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
    http_access_log:
        format: '%(remote_ip)s %(cid_resp_time)s "%(channel_name)s" [%(req_timestamp)s] "%(method)s %(path)s %(http_version)s" %(status_code)s %(response_size)s "-" "%(user_agent)s"'
    colour:
        format: '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
        (): zato.common.util.api.ColorFormatter

version: 1
""" # noqa: E501

# ################################################################################################################################
# ################################################################################################################################

# Based on http://stackoverflow.com/questions/384076/how-can-i-make-the-python-logging-output-to-be-colored
class ColorFormatter(Formatter):

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    RESET_SEQ = '\033[0m'
    COLOR_SEQ = '\033[1;%dm'
    BOLD_SEQ = '\033[1m'

    COLORS = {
      'WARNING': YELLOW,
      'INFO': WHITE,
      'DEBUG': BLUE,
      'CRITICAL': YELLOW,
      'ERROR': RED,
      'TRACE1': YELLOW
    }

    def __init__(self, fmt):
        self.use_color = True
        super(ColorFormatter, self).__init__(fmt)

# ################################################################################################################################

    def formatter_msg(self, msg, use_color=True):
        if use_color:
            msg = msg.replace('$RESET', self.RESET_SEQ).replace('$BOLD', self.BOLD_SEQ)
        else:
            msg = msg.replace('$RESET', '').replace('$BOLD', '')
        return msg

# ################################################################################################################################

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in self.COLORS:
            fore_color = 30 + self.COLORS[levelname]
            levelname_color = self.COLOR_SEQ % fore_color + levelname + self.RESET_SEQ
            record.levelname = levelname_color

        return Formatter.format(self, record)

# ################################################################################################################################
# ################################################################################################################################

def get_logging_conf_contents():
    # type: (str) -> str

    # We import it here to make CLI work faster
    from zato.common.util.platform_ import is_windows

    windows_log_handler_class     = 'logging.handlers.RotatingFileHandler'
    non_windows_log_handler_class = 'logging.handlers.ConcurrentRotatingFileHandler'

    # Under Windows, we cannot have multiple processes access the same log file
    log_handler_class = windows_log_handler_class if is_windows else non_windows_log_handler_class

    return logging_conf_contents.format(log_handler_class=log_handler_class)

# ################################################################################################################################
# ################################################################################################################################
