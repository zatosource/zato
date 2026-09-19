# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Live environment
from live_environment.parts import Parts, missing_requirements as _missing_requirements, skip_or_fail as _skip_or_fail, \
    tear_down

# Live HL7
from live_hl7.enmasse import import_definitions
from live_hl7.openhim.system import login as openhim_login
from live_hl7.openmrs.system import Admin_Username, REST_Path
from live_hl7.suite import Required_Variables, start_receiver, start_systems, start_zato

# Zato - the suite's own parts
from _enmasse import ExchangeAddresses, build_definitions
from _exchange import ExchangeChannels, configure_exchange, configure_shared_record
from _services import Recorders

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from hl7_client.mllp_receiver import MLLPReceiver
    from live_environment.quickstart import ZatoEnvironment
    from live_hl7.http import Session
    from live_hl7.system import Handle
    from zato.common.typing_ import strlist
    from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

# Setting this variable makes a machine without docker a failure rather than a skip, which is what a run
# that is meant to cover the exchange sets so that a machine without it is not passed silently.
Env_HIE_Required = 'Zato_Test_HL7_HIE'

# The systems the exchange is made of
OpenHIM_System = 'openhim'
OpenMRS_System = 'openmrs'

# What the rest of the suite takes from here
Parts = Parts
tear_down = tear_down

# ################################################################################################################################
# ################################################################################################################################

class HIEEnvironment(NamedTuple):
    """ Everything a test needs to know about the exchange it operates on.
    """

    # Facility B and the shared record's front door
    zato: 'ZatoEnvironment'
    client: 'AdminClient'

    # The interoperability layer, an API session on it and the ids of its channels
    openhim: 'Handle'
    openhim_session: 'Session'
    channels: 'ExchangeChannels'

    # The shared record and an API session on it
    openmrs: 'Handle'
    openmrs_session: 'Session'

    # The client registry - another system on the exchange, here the suite's own receiver
    registry: 'MLLPReceiver'

    # Where the front door records what reached it
    messages_file: 'str'

# ################################################################################################################################
# ################################################################################################################################

def missing_requirements() -> 'strlist':
    out = _missing_requirements(wants_docker=True, wants_haproxy=True, variables=Required_Variables)
    return out

# ################################################################################################################################

def skip_or_fail(missing:'strlist') -> 'None':
    _skip_or_fail(missing, Env_HIE_Required)

# ################################################################################################################################

def bring_up(parts:'Parts') -> 'HIEEnvironment':
    """ Brings the exchange up - Zato as facility B and the shared record's front door, HAProxy in front, the
    client registry, the interoperability layer and the shared record, each configured for the others.
    """

    # Facility B and the front door run in one Zato environment, HAProxy fronting the door on every
    # interface since the exchange connects from a container ..
    zato_parts = start_zato(parts, prefix='hie', recorders=Recorders)

    # .. the registry listens the same way ..
    registry = start_receiver(parts, 'the client registry')

    # .. the containers come up ..
    openhim, openmrs = start_systems(parts, (OpenHIM_System, OpenMRS_System))

    # .. the exchange learns its facilities and where the record and the registry are ..
    channels = configure_exchange(openhim, zato_parts.haproxy.ports.mllp_plain, registry.port, openhim.password)
    openmrs_session = configure_shared_record(openmrs)

    # .. and Zato learns where the exchange's channels and the record's queue are.
    addresses = ExchangeAddresses(
        national_adt=openhim.address('channel_1'),
        national_adt_registry_down=openhim.address('channel_2'),
        national_adt_shr_down=openhim.address('channel_3'),
        shr_host=openmrs.http_url('web'),
        shr_queue_path=REST_Path + '/hl7',
        shr_username=Admin_Username,
        shr_password=openmrs.password,
    )

    import_definitions(zato_parts.zato, build_definitions(addresses))

    out = HIEEnvironment(
        zato=zato_parts.zato,
        client=zato_parts.zato.client(),
        openhim=openhim,
        openhim_session=openhim_login(openhim),
        channels=channels,
        openmrs=openmrs,
        openmrs_session=openmrs_session,
        registry=registry,
        messages_file=zato_parts.messages_file,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
