# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from pathlib import Path

# Zato
from live_windows.containers import GuestInfo
from live_windows.enmasse import build_definitions
from live_windows.progress import Monitor
from live_windows.session import Sequences
from live_windows.settings import Accounts

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_windows.peer_server import PeerServer
    from live_windows.session import GuestHandle, handledict
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The module of services that the schedules and the job invoke, the same one that the live suites deploy
    Services_File = Path(__file__).parent.parent / 'smb_windows_live' / 'services' / 'file_exchange.py'

    # The prefix of the log file of the peer
    Log_Prefix = 'zato_smb_windows_peer_'

# ################################################################################################################################
# ################################################################################################################################

class PeerSuite:
    """ The peer in place of a Zato server, and a handle to each guest, for the whole session. It offers what
    the tests of the live suites use of their suite, so that the same tests run against the peer.
    """
    def __init__(self, peer:'PeerServer', handles:'handledict', started_versions:'strlist') -> 'None':
        self.peer = peer
        self.handles = handles
        self.started_versions = started_versions
        self.sequences = Sequences()

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
        """ Gives the peer the connections and the job of one guest, built by the same function as the enmasse files
        that the live suites import.
        """
        if not partner_version:
            partner_version = version

        if not target_version:
            target_version = version

        # The names of the connections and of the job follow the version, while the port follows the target
        target = self.handles[target_version].info
        partner = self.handles[partner_version].info

        guest = GuestInfo()
        guest.version = version
        guest.name = target.name
        guest.port = target.port

        definitions = build_definitions(
            guest,
            partner,
            password=password,
            is_landing_active=is_landing_active,
            has_contending_schedule=has_contending_schedule,
        )

        self.peer.import_definitions(version, definitions)

# ################################################################################################################################

    def import_all(self) -> 'None':
        for version in self.handles:
            self.import_guest(version)

# ################################################################################################################################

    def restart_server(self) -> 'None':
        self.peer.restart()

# ################################################################################################################################

    def new_monitor(self, name:'str') -> 'Monitor':
        handles = list(self.handles.values())

        out = Monitor(name, handles, self.peer.log_path)
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        self.peer.stop()

        for handle in self.handles.values():
            handle.close()

# ################################################################################################################################
# ################################################################################################################################
