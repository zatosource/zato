# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic

# gevent
from gevent.lock import RLock

# Zato
from zato.common.audit_log.api import AuditLog, AuditSource
from zato.common.audit_log.calls import record_remote_call
from zato.common.const import SECRETS
from zato.common.util.api import ping_odoo
from zato.server.connection.queue import ConnectionQueue

# Python 2/3 compatibility
from six import PY2

if PY2:
    import openerplib as client_lib # type: ignore
else:
    import odoolib as client_lib

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class OdooAuditedModel:
    """ Wraps one odoolib model so every method call - search, read, write, create
    and the rest - writes one audit event with its outcome and duration, the same
    shape REST outgoing records. A login refusal gets the auth-failed event type,
    because its remedy is different and alerting counts it separately.
    """
    def __init__(self, impl, conn_name, audit_log):
        self.impl = impl
        self.conn_name = conn_name
        self.audit_log = audit_log

    def __getattr__(self, name):

        target = getattr(self.impl, name)

        # Non-callable attributes, the model's name among them, pass through as they are
        if not callable(target):
            return target

        def proxy(*args, **kwargs):

            # What the event's status reports - which model operation ran
            status = '{}.{}'.format(self.impl.model_name, name)

            start = monotonic()

            # A failed call is recorded too, before the caller learns about it
            try:
                result = target(*args, **kwargs)
            except Exception as e:
                duration_ms = int((monotonic() - start) * 1000)
                is_auth_error = isinstance(e, client_lib.AuthenticationError)
                record_remote_call(self.audit_log, AuditSource.Odoo, self.conn_name,
                    is_ok=False, is_auth_error=is_auth_error, duration_ms=duration_ms,
                    status='{} -> {}'.format(status, e))
                raise

            duration_ms = int((monotonic() - start) * 1000)
            record_remote_call(self.audit_log, AuditSource.Odoo, self.conn_name,
                is_ok=True, duration_ms=duration_ms, status=status)

            return result

        return proxy

# ################################################################################################################################

class OdooAuditedConnection:
    """ Wraps one odoolib connection so the models it hands out record their calls -
    everything else passes through to the underlying connection unchanged.
    """
    def __init__(self, impl, conn_name, audit_log):
        self.impl = impl
        self.conn_name = conn_name
        self.audit_log = audit_log

    def get_model(self, model_name):
        model = self.impl.get_model(model_name)
        out = OdooAuditedModel(model, self.conn_name, self.audit_log)
        return out

    def __getattr__(self, name):
        out = getattr(self.impl, name)
        return out

# ################################################################################################################################

class OdooWrapper:
    """ Wraps a queue of connections to Odoo.
    """
    def __init__(self, config, server):
        self.config = config
        self.server = server

        # Decrypt the password if it is encrypted. It will be in clear text when the server is starting up
        # but otherwise for connections created in run-time, it will be decrypted.
        if self.config.password.startswith(SECRETS.PREFIX):
            self.config.password = self.server.decrypt(self.config.password)

        self.url = '{protocol}://{user}:******@{host}:{port}/{database}'.format(**self.config)
        self.client = ConnectionQueue(
            self.server,
            self.config.is_active,
            self.config.pool_size,
            self.config.queue_build_cap,
            self.config.id,
            self.config.name,
            'Odoo',
            self.url,
            self.add_client
        )

        self.update_lock = RLock()
        self.logger = getLogger(self.__class__.__name__)

        # Every model call of this connection is recorded here - what the alerting collectors read
        self.audit_log = AuditLog(self.server.name)

    def build_queue(self):
        with self.update_lock:
            self.client.build_queue()

    def add_client(self):

        conn = client_lib.get_connection(hostname=self.config.host, protocol=self.config.protocol, port=self.config.port,
            database=self.config.database, login=self.config.user, password=self.config.password)

        try:
            ping_odoo(conn)
        except Exception as e:
            logger.warning('Could not ping Odoo (%s), e:`%s`', self.config.name, e)

        # The connection goes into the queue wrapped, so the models it hands out record their calls
        conn = OdooAuditedConnection(conn, self.config.name, self.audit_log)

        _ = self.client.put_client(conn)

# ################################################################################################################################
