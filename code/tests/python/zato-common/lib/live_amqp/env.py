# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import contextmanager

# Zato
from zato.common.audit_log.api import get_audit_engine, ModuleCtx as AuditLogCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.test.rabbitmq_ import RabbitMQProcess

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def audit_log_env(directory:'str') -> 'envgen':
    """ Points the audit log at a private SQLite database for the duration of a test.
    """
    db_path = os.path.join(directory, 'audit.db')

    previous_type = os.environ.get(AuditLogCtx.Env_Type)
    previous_name = os.environ.get(AuditLogCtx.Env_Name)

    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = db_path

    # The first engine access creates the schema - it runs here, serially,
    # before any concurrent writers could race each other over the creation.
    _ = get_audit_engine()

    try:
        yield

    # Restore whatever the environment held before the test ran.
    finally:
        if previous_type is None:
            _ = os.environ.pop(AuditLogCtx.Env_Type, None)
        else:
            os.environ[AuditLogCtx.Env_Type] = previous_type

        if previous_name is None:
            _ = os.environ.pop(AuditLogCtx.Env_Name, None)
        else:
            os.environ[AuditLogCtx.Env_Name] = previous_name

# ################################################################################################################################

def get_broker_address(broker:'RabbitMQProcess') -> 'str':
    """ The broker's address without credentials - what a broker definition holds.
    """
    if broker.needs_ssl:
        scheme = 'amqps'
    else:
        scheme = 'amqp'

    out = f'{scheme}://127.0.0.1:{broker.amqp_port}//'
    return out

# ################################################################################################################################
# ################################################################################################################################
