# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

class Image:

    # The image that runs Windows under QEMU and KVM
    Name = 'dockurr/windows:6.06'

    # How long a guest has to shut down after a stop request
    Stop_Timeout = 120

# ################################################################################################################################
# ################################################################################################################################

class Versions:

    # The Windows Server releases the guests run
    Server_2025 = '2025'
    Server_2022 = '2022'

    All = Server_2025, Server_2022

# ################################################################################################################################
# ################################################################################################################################

class Guest:

    # The resources of each guest
    Disk_Size = '48G'
    RAM_Size  = '4G'
    CPU_Cores = '2'

    # The installation option of Windows Server
    Edition = 'core'

    # The port the SMB server of a guest listens on
    SMB_Port = 445

    # The prefix of the container and computer name of each guest
    Name_Prefix = 'zato-test-win'

    # A prepared disk older than this is built again, which keeps it within the evaluation period
    Max_Disk_Age_Days = 150

# ################################################################################################################################
# ################################################################################################################################

class Accounts:

    # The account the installation creates, a member of the local Administrators group
    Admin_Username = 'zatoadmin'
    Admin_Password = 'Zato.Admin.Test.1'

    # The account the test harness uses to reach the control share and to read the data shares
    Harness_Username = 'svc-harness'
    Harness_Password = 'Zato.Harness.Test.1'

    # The account Zato uses to reach the data shares
    Exchange_Username = 'svc-exchange'
    Exchange_Password = 'Zato.Exchange.Test.1'

# ################################################################################################################################
# ################################################################################################################################

class Paths:

    # The guest scripts that the installation copies into C:\OEM
    OEM_Dir = Path(__file__).parent / 'oem'

    # The agent that the harness uploads to each guest after it boots
    Agent_Path = Path(__file__).parent / 'agent' / 'agent.ps1'

    # Where the prepared disks are kept, one directory per Windows version
    Cache_Dir = Path(os.path.expanduser('~/.cache/zato-test-windows'))

    # Where the names and ports of running guests are recorded
    State_Path = Path('/tmp/zato-test-windows/state.json')

# ################################################################################################################################
# ################################################################################################################################

class Control:

    # The share through which the harness and the agent exchange commands and events
    Share = 'control'

    # The directory on each guest that holds the control share
    Local_Path = r'C:\shares\control'

    # The files and directories in the control share
    Provisioned  = 'provisioned.json'
    Provision_Error = 'provision-error.txt'
    Agent_Dir    = 'agent'
    Agent_Script = 'agent\\agent.ps1'
    Agent_Start  = 'agent\\start.json'
    Agent_Error  = 'agent-error.txt'
    Commands_Dir = 'commands'
    Events       = 'events.jsonl'
    Heartbeat    = 'heartbeat.json'

# ################################################################################################################################
# ################################################################################################################################

def storage_dir(version:'str') -> 'Path':
    """ Returns the directory that holds the prepared disk of one Windows version.
    """
    out = Paths.Cache_Dir / version / 'storage'
    return out

# ################################################################################################################################

def container_name(version:'str') -> 'str':
    """ Returns the name of the container that runs one Windows version.
    """
    out = f'{Guest.Name_Prefix}{version}'
    return out

# ################################################################################################################################
# ################################################################################################################################
