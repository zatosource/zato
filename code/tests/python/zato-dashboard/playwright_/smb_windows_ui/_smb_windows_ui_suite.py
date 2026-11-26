# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from live_windows.containers import GuestInfo
from live_windows.enmasse import build_definitions
from live_windows.progress import Monitor
from live_windows.settle import SettleBarrier
from live_windows.session import Sequences
from live_windows.settings import Accounts

# Playwright helpers
from server_restart import restart_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.session import GuestHandle, handledict
    from zato.common.typing_ import anydict, strlist
    from _dashboard_writer import DashboardWriter

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Where the server writes its log, relative to its directory
    Server_Log = os.path.join('logs', 'server.log')

# ################################################################################################################################
# ################################################################################################################################

class UISuite:
    """ The server and the Dashboard of the Playwright environment, and a handle to each guest, for the whole session.
    The definitions of each guest are created and changed through the Dashboard.
    """
    def __init__(
        self,
        zato_dashboard:'anydict',
        writer:'DashboardWriter',
        handles:'handledict',
        started_versions:'strlist',
        ) -> 'None':
        self.zato_dashboard = zato_dashboard
        self.writer = writer
        self.handles = handles
        self.started_versions = started_versions
        self.sequences = Sequences()

        self.server_log_path = os.path.join(zato_dashboard['server_dir'], ModuleCtx.Server_Log)

# ################################################################################################################################

    def guest(self, version:'str') -> 'GuestHandle':
        out = self.handles[version]
        return out

# ################################################################################################################################

    def definitions(
        self,
        version:'str',
        *,
        partner_version:'str'='',
        target_version:'str'='',
        password:'str'=Accounts.Exchange_Password,
        is_landing_active:'bool'=False,
        has_contending_schedule:'bool'=False,
        ) -> 'anydict':
        """ Returns the connections and the job of one guest. The partner drop may be on another guest,
        and the connections may point to another guest altogether, which is what a switchover does.
        """
        if not partner_version:
            partner_version = version

        if not target_version:
            target_version = version

        # The names of the connections and of the job follow the version, while the port follows the target.
        target = self.handles[target_version].info
        partner = self.handles[partner_version].info

        guest = GuestInfo()
        guest.version = version
        guest.name = target.name
        guest.port = target.port

        out = build_definitions(
            guest,
            partner,
            password=password,
            is_landing_active=is_landing_active,
            has_contending_schedule=has_contending_schedule,
        )

        return out

# ################################################################################################################################

    def apply_definitions(self, version:'str', definitions:'anydict') -> 'None':
        self.writer.apply(version, definitions)

# ################################################################################################################################

    def import_guest(
        self,
        version:'str',
        *,
        partner_version:'str'='',
        target_version:'str'='',
        password:'str'=Accounts.Exchange_Password,
        is_landing_active:'bool'=False,
        has_contending_schedule:'bool'=False,
        ) -> 'None':
        """ Brings the connections and the job of one guest in the Dashboard to their definitions.
        """
        definitions = self.definitions(
            version,
            partner_version=partner_version,
            target_version=target_version,
            password=password,
            is_landing_active=is_landing_active,
            has_contending_schedule=has_contending_schedule,
        )

        self.apply_definitions(version, definitions)

# ################################################################################################################################

    def import_all(self) -> 'None':
        """ Creates the default definitions of every guest, each with the partner drop on the same guest.
        """
        for version in self.handles:
            self.import_guest(version)

# ################################################################################################################################

    def restart_server(self) -> 'None':
        restart_server(self.zato_dashboard)

# ################################################################################################################################

    def new_monitor(self, name:'str') -> 'Monitor':
        handles = list(self.handles.values())
        barrier = SettleBarrier()

        out = Monitor(name, handles, self.server_log_path, barrier, self.expect_records)
        return out

# ################################################################################################################################

    def expect_records(self, *fragments:'str') -> 'None':
        """ Marks each server output line that contains any of the fragments as provoked deliberately,
        from now until the environment stops.
        """
        self.zato_dashboard['expected_records'].extend(fragments)

# ################################################################################################################################

    def close(self) -> 'None':
        for handle in self.handles.values():
            handle.close()

# ################################################################################################################################
# ################################################################################################################################
