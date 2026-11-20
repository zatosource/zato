# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
from time import time_ns
from urllib.parse import urlparse

# SQLAlchemy
from sqlalchemy import select

# OpenTelemetry
from opentelemetry.proto.common.v1.common_pb2 import InstrumentationScope
from opentelemetry.proto.resource.v1.resource_pb2 import Resource

# Zato
from zato.common.audit_log.common import event_attr_table, event_data, event_table
from zato.common.audit_log.export.data import has_data_export
from zato.common.audit_log.export.mapping import QueuedEvent, to_key_values
from zato.common.audit_log.export.queue import ExportQueue
from zato.common.audit_log.export.sender import sender_by_protocol
from zato.common.audit_log.export.state import ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.audit_log.export.config import ExportConfig
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

class AuditExport:
    """ Sends the audit events of one process to an OTLP collector.
    """

    def __init__(
        self,
        config:'ExportConfig',
        *,
        service_name:'str',
        server_name:'str',
        instance_id:'str',
        version:'str',
        ) -> 'None':

        self.config = config

        resource = self._build_resource(
            service_name=service_name,
            server_name=server_name,
            instance_id=instance_id,
            version=version,
        )

        parsed = urlparse(config.endpoint)
        address = f'{parsed.scheme}://{parsed.hostname}:{parsed.port}'

        sender_class = sender_by_protocol[config.protocol]
        sender = sender_class(config)

        scope = InstrumentationScope(name=ModuleCtx.Scope_Name, version=version)

        self.queue = ExportQueue(
            config=config,
            sender=sender,
            resource=resource,
            scope=scope,
            address=address,
        )

# ################################################################################################################################

    def _build_resource(
        self,
        *,
        service_name:'str',
        server_name:'str',
        instance_id:'str',
        version:'str',
        ) -> 'Resource':
        """ Builds the resource naming the process every record comes from.
        """
        attributes:'stranydict' = {
            'service.name': service_name,
            'service.instance.id': instance_id,
            'service.version': version,
            'zato.server.name': server_name,
            'host.name': socket.gethostname(),
            'process.pid': os.getpid(),
        }

        if self.config.environment:
            attributes['deployment.environment.name'] = self.config.environment

        attributes.update(self.config.resource_attributes)

        key_values = to_key_values(attributes)

        out = Resource(attributes=key_values)
        return out

# ################################################################################################################################

    def is_source_selected(self, source:'str') -> 'bool':
        """ Whether events of this source are exported.
        """
        if self.config.sources:
            out = source in self.config.sources
        else:
            out = True

        return out

# ################################################################################################################################

    def emit(
        self,
        event_id:'int',
        values:'stranydict',
        attrs:'stranydict',
        *,
        bodies:'stranydict',
        is_payload_active:'bool',
        ) -> 'None':
        """ Hands one written event to the export. Only filters and appends - the record is built by the worker.
        """
        source = values['source']

        # A source that is not selected is not exported ..
        if not self.is_source_selected(source):
            return

        # .. a payload is not kept in the queue unless it is going to be sent ..
        if not is_payload_active:
            if not has_data_export(source, values['event_type']):
                values = dict(values)
                values['data'] = ''
            bodies = {}

        event = QueuedEvent()
        event.event_id = event_id
        event.values = values
        event.attrs = attrs
        event.bodies = bodies
        event.observed_ns = time_ns()
        event.is_payload_active = is_payload_active

        # .. and the event joins the queue.
        self.queue.add(event)

# ################################################################################################################################

    def emit_batch(self, batch:'pending_event_list') -> 'None':
        """ Hands a batch of events the database accepted to the export.
        """
        for pending in batch:
            self.emit(
                pending.event_id,
                pending.values,
                pending.attrs,
                bodies=pending.bodies,
                is_payload_active=pending.is_export_payload_active,
            )

# ################################################################################################################################

    def emit_row(self, engine:'Engine', event_id:'int') -> 'None':
        """ Reads an event updated in place back from the database and hands it to the export again.
        """
        event_query = select(event_table, event_data).where(event_table.c.id == event_id)
        attr_query = select(event_attr_table).where(event_attr_table.c.event_id == event_id)

        with engine.begin() as connection:
            row = connection.execute(event_query).mappings().first()
            attr_rows = connection.execute(attr_query).mappings().all()

        # A row that was never written means the audit log was off at the time
        if row is None:
            return

        values = dict(row)
        attrs:'stranydict' = {}

        # Numbers come back as numbers, everything else as the string it was stored as
        for attr_row in attr_rows:
            if (value_number := attr_row['value_number']) is not None:
                attrs[attr_row['name']] = value_number
            else:
                attrs[attr_row['name']] = attr_row['value']

        self.emit(event_id, values, attrs, bodies={}, is_payload_active=False)

# ################################################################################################################################

    def flush_and_stop(self) -> 'None':
        """ Sends what is queued for at most the export timeout and stops the export.
        """
        timeout_seconds = self.config.timeout_ms / 1000
        self.queue.flush_and_stop(timeout_seconds)

# ################################################################################################################################
# ################################################################################################################################
