# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How an HL7 live suite brings up its parts - Zato with HAProxy in front, the containers of the systems it
# works with and its own MLLP receivers, each registered with the suite's Parts for one tear_down to end.

# stdlib
import os
import tempfile
from typing import NamedTuple

# Live environment
from live_environment.haproxy import Every_Interface, start_haproxy
from live_environment.quickstart import ZatoEnvironment

# Live HL7
from hl7_client.mllp_receiver import MLLPReceiver
from live_hl7.credentials import Password_Env
from live_hl7.recording import Messages_File_Variable, Service_File_Name, build_source
from live_hl7.runner import start as start_system, stop_handle

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
    bind_address:'str'=Every_Interface,
    tls_bind:'TLSBind | None'=None,
    ) -> 'ZatoParts':
    """ A throwaway Zato environment with the recording services deployed and HAProxy in front of its MLLP
    listener, on every interface by default.
    """
    directory = tempfile.mkdtemp(prefix=f'zato_hl7_{prefix}_')
    messages_file = os.path.join(directory, 'messages.txt')

    zato = ZatoEnvironment(directory, password_prefix=f'test.hl7.{prefix}')
    zato.create()
    zato.start({Messages_File_Variable: messages_file})
    parts.add('Zato', zato.stop)

    zato.deploy(Service_File_Name, build_source(recorders))

    haproxy = start_haproxy(directory, zato.mllp_internal_port, bind_address=bind_address, tls_bind=tls_bind)
    parts.add('HAProxy', haproxy.stop)

    out = ZatoParts(zato, haproxy, directory, messages_file)
    return out

# ################################################################################################################################

def start_systems(parts:'Parts', names:'strtuple', *, environments:'environments_dict | None'=None) -> 'handle_list':
    """ The containers of the named systems, in the order given, each with whatever extra environment
    the suite has for it, keyed by the system's name.
    """
    if environments is None:
        environments = {}

    out:'handle_list' = []

    for name in names:

        if name in environments:
            extra_environment = environments[name]
        else:
            extra_environment = {}

        handle = start_system(name, is_standalone=False, extra_environment=extra_environment)
        parts.add(name, lambda handle=handle: stop_handle(handle))
        out.append(handle)

    return out

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
