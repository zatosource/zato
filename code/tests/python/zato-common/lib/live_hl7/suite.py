# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How an HL7 live suite brings up its parts - Zato with HAProxy in front, the containers of the systems it
# works with and its own MLLP receivers, each registered with the suite's Parts for one tear_down to end.

# stdlib
import os
import subprocess
import tempfile
from functools import partial
from typing import NamedTuple

# Live environment
from live_environment.haproxy import Every_Interface, start_haproxy
from live_environment.quickstart import ZatoEnvironment

# Live HL7
from hl7_client.mllp_receiver import MLLPReceiver
from live_hl7.credentials import Password_Env
from live_hl7.extension import Extension_Root_Env
from live_hl7.recording import Messages_File_Variable, Service_File_Name, build_source
from live_hl7.registry import is_extension_system
from live_hl7.runner import Extra_Environment_Prefix, Fresh_Env, Fresh_Wanted, attach

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.haproxy import HAProxyHandle, TLSBind
    from live_environment.parts import Parts
    from live_hl7.recording import recorder_list
    from live_hl7.system import Handle
    from zato.common.typing_ import strstrdict, strtuple

# ################################################################################################################################
# ################################################################################################################################

# What every HL7 live suite needs set before it can start any of its systems
Required_Variables = (Password_Env,)

# System name to the extra environment its containers start with
environments_dict = dict[str, 'strstrdict']

# A suite starts its systems standalone through the Make targets a person uses, so a run of the suite is a run
# of those targets too - the public ones under this root, the extension's under its own - and each as new,
# without what an earlier run left in it
Public_Root_Env = 'ZATO_TEST_BASE_DIR'
Start_Target_Prefix = 'hl7-start-'
Stop_Target_Prefix = 'hl7-stop-'

# Where a suite writes down what a run showed about a system that a test cannot decide for it
Findings_File_Name = 'findings.txt'

# ################################################################################################################################
# ################################################################################################################################

class ZatoParts(NamedTuple):
    """ Zato and what fronts it, as one suite started them.
    """
    zato: 'ZatoEnvironment'
    haproxy: 'HAProxyHandle'
    directory: 'str'
    messages_file: 'str'

# ################################################################################################################################

handle_list = list['Handle']

# ################################################################################################################################
# ################################################################################################################################

def start_zato(
    parts:'Parts',
    *,
    prefix:'str',
    recorders:'recorder_list',
    sources:'strtuple'=(),
    bind_address:'str'=Every_Interface,
    tls_bind:'TLSBind | None'=None,
    ) -> 'ZatoParts':
    """ A throwaway Zato environment with the recording services and the suite's own deployed and HAProxy in front
    of its MLLP listener, on every interface by default.
    """
    directory = tempfile.mkdtemp(prefix=f'zato_hl7_{prefix}_')
    messages_file = os.path.join(directory, 'messages.txt')

    zato = ZatoEnvironment(directory, password_prefix=f'test.hl7.{prefix}')
    zato.create()
    zato.start({Messages_File_Variable: messages_file})
    parts.add('Zato', zato.stop)

    zato.deploy(Service_File_Name, build_source(recorders, sources))

    haproxy = start_haproxy(directory, zato.mllp_internal_port, bind_address=bind_address, tls_bind=tls_bind)
    parts.add('HAProxy', haproxy.stop)

    out = ZatoParts(zato, haproxy, directory, messages_file)
    return out

# ################################################################################################################################

def start_systems(parts:'Parts', names:'strtuple', *, environments:'environments_dict | None'=None) -> 'handle_list':
    """ The named systems, in the order given, each started fresh through its Make target with whatever extra
    environment the suite has for it, keyed by the system's name, and stopped through its Make target at the end.
    """
    if environments is None:
        environments = {}

    out:'handle_list' = []

    for name in names:

        # The start is a fresh one, the extra environment travels the way the target's command takes it
        start_environment = {Fresh_Env: Fresh_Wanted}

        if name in environments:
            for key, value in environments[name].items():
                start_environment[Extra_Environment_Prefix + key] = value

        _make(name, Start_Target_Prefix, start_environment)
        parts.add(name, partial(_make, name, Stop_Target_Prefix, {}))

        handle = attach(name)
        out.append(handle)

    return out

# ################################################################################################################################

def _make_root(name:'str') -> 'str':
    if is_extension_system(name):
        out = os.environ[Extension_Root_Env]
    else:
        out = os.environ[Public_Root_Env]

    return out

# ################################################################################################################################

def _make(name:'str', target_prefix:'str', process_environment:'strstrdict') -> 'None':
    """ Runs a system's Make target with the given variables added to the process environment.
    """
    environment = dict(os.environ)
    environment.update(process_environment)

    root = _make_root(name)
    target = target_prefix + name
    print(f'make {target} in {root}', flush=True)

    _ = subprocess.run(['make', '-C', root, target], env=environment, check=True)

# ################################################################################################################################

def record_finding(directory:'str', text:'str') -> 'None':
    """ Something the run showed about a system, kept next to everything else of the run and printed
    for whoever watches it.
    """
    path = os.path.join(directory, Findings_File_Name)

    with open(path, 'a') as file_handle:
        _ = file_handle.write(text + '\n')

    print(f'Finding: {text}')

# ################################################################################################################################

def start_receiver(
    parts:'Parts',
    what:'str',
    *,
    ack_code:'str'='AA',
    cert_path:'str'='',
    key_path:'str'='',
    ca_path:'str'='',
    ) -> 'MLLPReceiver':
    """ One MLLP receiver standing in for a system the suite has no container for, listening where
    containers can reach it.
    """
    out = MLLPReceiver(
        ack_code=ack_code,
        cert_path=cert_path,
        key_path=key_path,
        ca_path=ca_path,
        host=Every_Interface,
    )

    out.start()
    parts.add(what, out.stop)

    return out

# ################################################################################################################################
# ################################################################################################################################
