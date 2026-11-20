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

    # The guests, each a Windows Server release installed in one language
    Server_2025          = '2025'
    Server_2022          = '2022'
    Server_2019          = '2019'
    Server_2025_Japanese = '2025ja'

    All = Server_2025, Server_2022, Server_2019, Server_2025_Japanese

# The guest that a test of each version uses as its second guest
Partners = {
    Versions.Server_2025:          Versions.Server_2022,
    Versions.Server_2022:          Versions.Server_2025,
    Versions.Server_2019:          Versions.Server_2025_Japanese,
    Versions.Server_2025_Japanese: Versions.Server_2019,
}

class Language:

    # The installation languages, in the form the container image accepts them
    English  = 'en'
    Japanese = 'ja'

# The Windows Server release and the installation language of each guest
Media = {
    Versions.Server_2025:          ('2025', Language.English),
    Versions.Server_2022:          ('2022', Language.English),
    Versions.Server_2019:          ('2019', Language.English),
    Versions.Server_2025_Japanese: ('2025', Language.Japanese),
}

# ################################################################################################################################
# ################################################################################################################################

class Guest:

    # The resources of each guest
    Disk_Size = '48G'
    RAM_Size  = '4G'
    CPU_Cores = '2'

    # The CPU features that QEMU adds after those of the image. QEMU does not save the state of a guest
    # whose CPU has an invariant TSC or passes every Hyper-V enlightenment of the host through, so the guests
    # run without an invariant TSC, with the Hyper-V enlightenments of the image turned off and an explicit set in their place.
    CPU_Flags = '-invtsc,hv-relaxed,hv-vapic,hv-spinlocks=0x1fff,hv-vpindex,hv-runtime,hv-time,hv-synic,hv-stimer,' \
        'hv-frequencies,hv-tlbflush,hv-ipi'
    Hyper_V   = 'N'

    # The installation option of Windows Server
    Edition = 'core'

    # The port the SMB server of a guest listens on
    SMB_Port = 445

    # The prefix of the container name of each guest
    Name_Prefix = 'zato-test-win'

    # The prefix of the Windows computer name of each guest, which Windows limits to 15 characters
    Computer_Prefix = 'zatowin'

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

    # Where the installation media are kept, one ISO file per Windows version
    ISO_Dir = Path(os.path.expanduser('~/files/iso'))

    # Where the names and ports of running guests are recorded, one file per instance
    State_Dir = Path('/tmp/zato-test-windows')

    # Where the storage directory of each running guest is kept, one directory per guest
    Instances_Dir = Cache_Dir / 'instances'

# ################################################################################################################################
# ################################################################################################################################

class Control:

    # The share through which the harness and the agent exchange commands and events
    Share = 'control'

    # The directory on each guest that holds the control share
    Local_Path = r'C:\shares\control'

    # The files and directories in the control share
    Provisioned     = 'provisioned.json'
    Provision_Error = 'provision-error.txt'
    Agent_Dir       = 'agent'
    Agent_Script    = 'agent\\agent.ps1'
    Agent_Start     = 'agent\\start.json'
    Agent_Error     = 'agent-error.txt'
    Commands_Dir    = 'commands'
    Events          = 'events.jsonl'
    Heartbeat       = 'heartbeat.json'

# ################################################################################################################################
# ################################################################################################################################

class Suite:

    # The variable that, set to 1, makes a missing requirement of the live suites a failure rather than a skip
    Required_Variable = 'Zato_Test_SMB_Windows'

    # The device that QEMU runs the guests with
    KVM_Device = '/dev/kvm'

class Instance:

    # The variable that names the guests of one test process, so that processes that run at the same time
    # each run guests of their own. The guests of a process without it have the names of their versions only.
    Variable = 'Zato_Test_SMB_Instance'

    # The name of the guests of a process without the variable
    Unnamed = ''

class Shards:

    # The variable that names the shard of the tests that a test process runs, as its index and the number of shards, e.g. 3/8
    Variable = 'Zato_Test_SMB_Shard'
    Separator = '/'

    # The variable with the number of shards that the driver runs, a multiple of the number of versions,
    # and the number it runs without the variable
    Count_Variable = 'Zato_Test_SMB_Shards'
    Default_Count  = 8

class Step:

    # The variable that names the version whose tests a session of the Dashboard suite runs
    Variable = 'Zato_Test_SMB_UI_Version'

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

def current_instance() -> 'str':
    """ Returns the name of the guests of this process.
    """
    if name := os.environ.get(Instance.Variable):
        out = name
    else:
        out = Instance.Unnamed

    return out

# ################################################################################################################################

def _instance_suffix(instance:'str') -> 'str':
    if instance:
        out = f'-{instance}'
    else:
        out = Instance.Unnamed

    return out

# ################################################################################################################################

def guest_name(version:'str', instance:'str') -> 'str':
    """ Returns the name of the container that runs the guest of one Windows version for one instance.
    """
    name = container_name(version)
    suffix = _instance_suffix(instance)

    out = f'{name}{suffix}'
    return out

# ################################################################################################################################

def instance_dir(version:'str', instance:'str') -> 'Path':
    """ Returns the storage directory of the guest of one Windows version for one instance.
    """
    suffix = _instance_suffix(instance)

    out = Paths.Instances_Dir / f'{version}{suffix}'
    return out

# ################################################################################################################################

def state_path(instance:'str') -> 'Path':
    """ Returns the file that records the running guests of one instance.
    """
    suffix = _instance_suffix(instance)

    out = Paths.State_Dir / f'state{suffix}.json'
    return out

# ################################################################################################################################

def computer_name(version:'str') -> 'str':
    """ Returns the Windows computer name of the guest that runs one Windows version.
    """
    out = f'{Guest.Computer_Prefix}{version}'
    return out

# ################################################################################################################################

def iso_name(version:'str') -> 'str':
    """ Returns the name under which the container stores the installation media of one guest,
    e.g. win2025-eval.iso or win2025-eval_ja.iso.
    """
    release, language = Media[version]

    out = f'win{release}-eval'

    if language != Language.English:
        out = f'{out}_{language}'

    out = f'{out}.iso'
    return out

# ################################################################################################################################
# ################################################################################################################################
