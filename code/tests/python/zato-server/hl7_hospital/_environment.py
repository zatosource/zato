# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from typing import NamedTuple

# Live environment
from live_environment.haproxy import TLSBind
from live_environment.parts import Parts, missing_requirements as _missing_requirements, skip_or_fail as _skip_or_fail, \
    tear_down

# Live HL7
from live_hl7.compose import Host_Gateway
from live_hl7.dcm4chee.system import add_hl7_receiver, configure_hl7_tls, set_hl7_send_retries, tls_environment
from live_hl7.enmasse import TLSClient, import_definitions
from live_hl7.suite import Required_Variables, start_receiver, start_systems, start_zato
from live_hl7.tls import Authority, new_stranger

# Zato - the suite's own parts
from _enmasse import HospitalAddresses, build_definitions
from _messages import Engine_Application, Hospital_Facility
from _services import Recorders

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from hl7_client.mllp_receiver import MLLPReceiver
    from live_environment.quickstart import ZatoEnvironment
    from live_hl7.system import Handle
    from live_hl7.tls import Identity
    from zato.common.typing_ import strlist
    from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

# Setting this variable makes a machine without docker a failure rather than a skip
Env_Hospital_Required = 'Zato_Test_HL7_Hospital'

# The one container of the scenario
PACS_System = 'dcm4chee'

# How the PACS knows the engine - a device per listener of the engine, each with an HL7 application on it,
# the names the archive addresses in MSH-5 and MSH-6 of everything it publishes
Engine_Device = 'zato'
Engine_Receiver = f'{Engine_Application}|{Hospital_Facility}'

Engine_TLS_Device = 'zato-tls'
Engine_TLS_Receiver = f'{Engine_Application}_TLS|{Hospital_Facility}'

# A receiver presenting a certificate the suite's authority did not issue - what the PACS is to refuse
Stranger_Device = 'stranger'
Stranger_Receiver = f'STRANGER|{Hospital_Facility}'
Stranger_Identity_Name = 'somebody-else'

# How many times the PACS tries a message its receiver could not be reached for - none, so that a test
# waiting on the failure sees it at once
PACS_Send_Retries = 0

# Whom the suite's authority issues certificates to and the names they are connected by
Authority_Name = 'Hospital Test Authority'
Engine_Identity_Name = 'zato-integration-engine'
PACS_Identity_Name = 'hospital-pacs'

Engine_Host_Names = ['localhost', '127.0.0.1', Host_Gateway]
PACS_Host_Names = ['localhost', '127.0.0.1']

# ################################################################################################################################
# ################################################################################################################################

class HospitalEnvironment(NamedTuple):
    """ Everything a test needs to know about the hospital it operates in.
    """

    # The integration engine
    zato: 'ZatoEnvironment'
    client: 'AdminClient'

    # Where senders reach the engine - the plain port the PACS publishes to, the TLS port a department
    # outside the network publishes to
    engine_plain_port: 'int'
    engine_tls_port: 'int'

    # The PACS
    pacs: 'Handle'

    # The second department - a receiver of its own
    department: 'MLLPReceiver'

    # A receiver over TLS with a certificate from elsewhere
    stranger: 'MLLPReceiver'

    # The suite's authority and the identities it issued
    authority: 'Authority'
    engine_identity: 'Identity'
    pacs_identity: 'Identity'

    # Where the engine's recording services write and where everything else of the suite is
    messages_file: 'str'
    directory: 'str'

# ################################################################################################################################
# ################################################################################################################################

def missing_requirements() -> 'strlist':
    out = _missing_requirements(wants_docker=True, wants_haproxy=True, variables=Required_Variables)
    return out

# ################################################################################################################################

def skip_or_fail(missing:'strlist') -> 'None':
    _skip_or_fail(missing, Env_Hospital_Required)

# ################################################################################################################################

def bring_up(parts:'Parts') -> 'HospitalEnvironment':
    """ Brings the hospital up - the authority and its identities, the engine with HAProxy and its TLS bind, the
    second department and the PACS, each configured for the others.
    """
    directory = tempfile.mkdtemp(prefix='zato_hl7_hospital_')

    # The certificates of the run ..
    authority = Authority(os.path.join(directory, 'tls'), Authority_Name)
    engine_identity = authority.issue('engine', Engine_Identity_Name, host_names=Engine_Host_Names)
    pacs_identity = authority.issue('pacs', PACS_Identity_Name, host_names=PACS_Host_Names)

    # .. the engine, with the door a department outside the network comes through ..
    tls_bind = TLSBind(pem_path=engine_identity.combined_pem_path, ca_cert_path=authority.ca_cert_path)
    zato_parts = start_zato(parts, prefix='hospital', recorders=Recorders, tls_bind=tls_bind)

    # .. the second department, and a receiver nobody here vouches for ..
    department = start_receiver(parts, 'the department')

    stranger_identity = new_stranger(directory, 'stranger', Stranger_Identity_Name)
    stranger = start_receiver(
        parts,
        'the stranger',
        cert_path=stranger_identity.cert_path,
        key_path=stranger_identity.key_path,
    )

    # .. the PACS, presenting what the authority issued it and trusting what the authority issued ..
    environments = {PACS_System: tls_environment(authority, pacs_identity)}
    pacs, = start_systems(parts, (PACS_System,), environments=environments)

    # .. the PACS switches its TLS listener to cipher suites the engine offers, gives up on an unreachable
    # receiver at once and learns the engine's two doors ..
    configure_hl7_tls(pacs)
    set_hl7_send_retries(pacs, PACS_Send_Retries)

    plain_port = zato_parts.haproxy.ports.mllp_plain
    tls_port = zato_parts.haproxy.ports.mllp_tls

    add_hl7_receiver(pacs, Engine_Device, Engine_Receiver, Host_Gateway, plain_port)
    add_hl7_receiver(pacs, Engine_TLS_Device, Engine_TLS_Receiver, Host_Gateway, tls_port, is_tls=True)
    add_hl7_receiver(pacs, Stranger_Device, Stranger_Receiver, Host_Gateway, stranger.port, is_tls=True)

    # .. and the engine learns where the PACS and the department are.
    addresses = HospitalAddresses(
        pacs=pacs.address('hl7'),
        pacs_tls=pacs.address('hl7_tls'),
        department=department.address,
        tls=TLSClient(authority.ca_cert_path, engine_identity.cert_path, engine_identity.key_path),
    )

    import_definitions(zato_parts.zato, build_definitions(addresses))

    out = HospitalEnvironment(
        zato=zato_parts.zato,
        client=zato_parts.zato.client(),
        engine_plain_port=plain_port,
        engine_tls_port=tls_port,
        pacs=pacs,
        department=department,
        stranger=stranger,
        authority=authority,
        engine_identity=engine_identity,
        pacs_identity=pacs_identity,
        messages_file=zato_parts.messages_file,
        directory=directory,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

# What the rest of the suite takes from here
Parts = Parts
tear_down = tear_down

# ################################################################################################################################
# ################################################################################################################################
