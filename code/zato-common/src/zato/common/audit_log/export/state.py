# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from importlib import import_module
from logging import getLogger

# Zato
from zato.common.audit_log.export.config import get_export_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.export.api import AuditExport

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The instrumentation scope every record is emitted under
    Scope_Name = 'zato.audit_log'

    # What the server and the dashboard call themselves
    Service_Server    = 'zato-server'
    Service_Dashboard = 'zato-dashboard'

    # The module of the export, imported only when an endpoint is configured
    API_Module_Name = 'zato.common.audit_log.export.api'

# ################################################################################################################################
# ################################################################################################################################

# The export of this process, if it has one
_export:'AuditExport | None' = None

# ################################################################################################################################

def get_audit_export() -> 'AuditExport | None':
    """ Returns the export of this process, or None when the export is off.
    """
    return _export

# ################################################################################################################################

def set_audit_export(export:'AuditExport | None') -> 'None':
    """ Registers the export of this process.
    """
    global _export
    _export = export

# ################################################################################################################################

def start_audit_export(
    *,
    service_name:'str',
    server_name:'str',
    instance_id:'str',
    version:'str',
    ) -> 'AuditExport | None':
    """ Builds the export of this process from the environment and registers it, or leaves the export off
    when no endpoint is set or the configuration cannot be read.
    """
    try:
        config = get_export_config()
    except Exception as e:
        logger.warning('Audit export is off - %s', e)
        return None

    if not config:
        return None

    # The module of the export is imported once an endpoint is configured ..
    api = import_module(ModuleCtx.API_Module_Name)

    # .. the export is built from the configuration ..
    out:'AuditExport' = api.AuditExport(
        config,
        service_name=service_name,
        server_name=server_name,
        instance_id=instance_id,
        version=version,
    )

    # .. and registered as the export of this process.
    set_audit_export(out)

    logger.info('Audit export to %s is on, sources: %s', out.queue.address, sorted(config.sources) or 'all')

    return out

# ################################################################################################################################

def stop_audit_export() -> 'None':
    """ Flushes and stops the export of this process, if it has one.
    """
    if export := get_audit_export():
        export.flush_and_stop()
        set_audit_export(None)

# ################################################################################################################################
# ################################################################################################################################
