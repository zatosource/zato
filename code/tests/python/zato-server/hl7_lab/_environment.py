# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import NamedTuple

# Live environment
from live_environment.parts import Parts, missing_requirements as _missing_requirements, \
    skip_or_fail as _skip_or_fail, tear_down

# Live HL7
from live_hl7.enmasse import import_definitions
from live_hl7.openelis.system import loinc_test_id, login, point_analyzer_at, zato_analyzer
from live_hl7.suite import Required_Variables, start_systems, start_zato

# Zato - the suite's own parts
from _enmasse import build_definitions
from _messages import Haemoglobin_LOINC
from _services import Recorders

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from live_hl7.http import Session
    from live_hl7.system import Handle
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# Setting this variable makes a machine without docker a failure rather than a skip
Env_Lab_Required = 'Zato_Test_HL7_Lab'

# The one container of the scenario
LIS_System = 'openelis'

# ################################################################################################################################
# ################################################################################################################################

class LabEnvironment(NamedTuple):
    """ Everything a test needs to know about the laboratory it operates in.
    """

    # The middleware
    zato: 'ZatoEnvironment'

    # Where analyzers reach the middleware
    middleware_port: 'int'

    # The LIS, a session with it, Zato as the analyzer it registered and the test every order here is for
    lis: 'Handle'
    session: 'Session'
    analyzer_id: 'str'
    test_id: 'str'

    # Where the middleware's recording service writes
    messages_file: 'str'

# ################################################################################################################################
# ################################################################################################################################

def missing_requirements() -> 'strlist':
    out = _missing_requirements(wants_docker=True, wants_haproxy=True, variables=Required_Variables)
    return out

# ################################################################################################################################

def skip_or_fail(missing:'strlist') -> 'None':
    _skip_or_fail(missing, Env_Lab_Required)

# ################################################################################################################################

def bring_up(parts:'Parts') -> 'LabEnvironment':
    """ Brings the laboratory up - the middleware with HAProxy in front and the LIS, each configured for the other.
    """

    # The middleware ..
    zato_parts = start_zato(parts, prefix='lab', recorders=Recorders)

    # .. the LIS, which registered Zato as its analyzer on the way up ..
    lis, = start_systems(parts, (LIS_System,))

    # .. whose orders go to the middleware from now on ..
    session = login(lis)
    analyzer = zato_analyzer(session)

    middleware_port = zato_parts.haproxy.ports.mllp_plain
    point_analyzer_at(session, lis, analyzer, middleware_port)

    # .. and the middleware learns where the LIS takes results.
    import_definitions(zato_parts.zato, build_definitions(lis.address('mllp')))

    out = LabEnvironment(
        zato=zato_parts.zato,
        middleware_port=middleware_port,
        lis=lis,
        session=session,
        analyzer_id=analyzer['id'],
        test_id=loinc_test_id(lis, Haemoglobin_LOINC),
        messages_file=zato_parts.messages_file,
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

# What the rest of the suite takes from here
Parts = Parts
tear_down = tear_down

# ################################################################################################################################
# ################################################################################################################################
