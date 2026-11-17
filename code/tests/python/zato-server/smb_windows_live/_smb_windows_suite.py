# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from pathlib import Path

# Zato
from live_windows.containers import GuestInfo
from live_windows.enmasse import build_yaml
from live_windows.progress import Monitor
from live_windows.session import Sequences
from live_windows.settings import Accounts

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from live_environment.scheduler import SchedulerProcess
    from live_windows.session import GuestHandle, handledict
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The module of services that the schedules and the job invoke
    Services_File = Path(__file__).parent / 'services' / 'file_exchange.py'

    # Where the server writes its log, relative to its directory
    Server_Log = os.path.join('logs', 'server.log')

    # The prefix of the directory of the environment and of its password
    Directory_Prefix = 'zato_smb_windows_'
    Password_Prefix  = 'test.smb.windows'

# ################################################################################################################################
# ################################################################################################################################

class SMBWindowsSuite:
    """ One Zato server with a private scheduler, and a handle to each guest, for the whole session.
    """
    def __init__(
        self,
        zato:'ZatoEnvironment',
        scheduler:'SchedulerProcess',
        handles:'handledict',
        started_versions:'strlist',
        ) -> 'None':
        self.zato = zato
        self.scheduler = scheduler
        self.handles = handles
        self.started_versions = started_versions
        self.sequences = Sequences()
        self.import_count = 0

        self.server_log_path = os.path.join(zato.server_directory, ModuleCtx.Server_Log)

# ################################################################################################################################

    def guest(self, version:'str') -> 'GuestHandle':
        out = self.handles[version]
        return out

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
        """ Imports the connections and the job of one guest. The partner drop may be on another guest,
        and the connections may point to another guest altogether, which is what a switchover does.
        """
        if not partner_version:
            partner_version = version

        if not target_version:
            target_version = version

        # The names of the connections and of the job follow the version, while the port follows the target ..
        target = self.handles[target_version].info
        partner = self.handles[partner_version].info

        guest = GuestInfo()
        guest.version = version
        guest.name = target.name
        guest.port = target.port

        definitions = build_yaml(
            guest,
            partner,
            password=password,
            is_landing_active=is_landing_active,
            has_contending_schedule=has_contending_schedule,
        )

        # .. and each import gets a file of its own, which a failing run can be read from.
        self.import_count += 1
        file_name = f'smb-win{version}-{self.import_count}.yaml'

        _ = self.zato.import_yaml(file_name, definitions)

# ################################################################################################################################

    def import_all(self) -> 'None':
        """ Imports the default definitions of every guest, each with the partner drop on the same guest.
        """
        for version in self.handles:
            self.import_guest(version)

# ################################################################################################################################

    def restart_server(self) -> 'None':
        self.zato.restart(self.scheduler.server_environment())

# ################################################################################################################################

    def new_monitor(self, name:'str') -> 'Monitor':
        handles = list(self.handles.values())

        out = Monitor(name, handles, self.server_log_path)
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        for handle in self.handles.values():
            handle.close()

# ################################################################################################################################
# ################################################################################################################################
