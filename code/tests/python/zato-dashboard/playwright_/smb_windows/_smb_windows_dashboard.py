# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# PyYAML
import yaml

# Zato
from live_windows.containers import stop_guests
from live_windows.enmasse import build_definitions
from live_windows.progress import Monitor
from live_windows.session import Sequences

# Playwright helpers
from mcp_gateway_live import import_enmasse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.session import GuestHandle, handledict
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Where the server writes its log, relative to its directory
    Server_Log = os.path.join('logs', 'server.log')

# ################################################################################################################################
# ################################################################################################################################

class DashboardSuite:
    """ The guests, as reached from the server of the Dashboard environment.
    """
    def __init__(self, zato_dashboard:'anydict', handles:'handledict', started_versions:'strlist') -> 'None':
        self.zato_dashboard = zato_dashboard
        self.handles = handles
        self.started_versions = started_versions
        self.sequences = Sequences()
        self.server_log_path = os.path.join(zato_dashboard['server_dir'], ModuleCtx.Server_Log)

# ################################################################################################################################

    def guest(self, version:'str') -> 'GuestHandle':
        out = self.handles[version]
        return out

# ################################################################################################################################

    def definitions(self, version:'str') -> 'anydict':
        """ Returns the default definitions of one guest, with the partner drop on the same guest.
        """
        info = self.handles[version].info

        out = build_definitions(info, info)
        return out

# ################################################################################################################################

    def import_definitions(self, definitions:'anydict') -> 'None':
        text = yaml.safe_dump(definitions, sort_keys=False)
        import_enmasse(self.zato_dashboard, text)

# ################################################################################################################################

    def import_guest(self, version:'str') -> 'None':
        definitions = self.definitions(version)
        self.import_definitions(definitions)

# ################################################################################################################################

    def new_monitor(self, name:'str') -> 'Monitor':
        handles = list(self.handles.values())

        out = Monitor(name, handles, self.server_log_path)
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Closes the connections to the guests, and removes the guests this session booted.
        """
        for handle in self.handles.values():
            handle.close()

        # No guest is left running once the session ends
        guest_versions = list(self.handles)
        stop_guests(guest_versions)

# ################################################################################################################################
# ################################################################################################################################
