# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

String constants containing the Python source of each test service.
These are written to the Zato pickup directory by the hot_deploy_services fixture in conftest.py.
"""

# ################################################################################################################################
# ################################################################################################################################

echo_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# The file where received messages are stored, one JSON string per line.
# A file is used because hot-deployed service modules do not share module-level state.
_messages_file = os.environ['Zato_Test_MLLP_Messages_File']

# ################################################################################################################################
# ################################################################################################################################

class TestHL7MLLPEcho(Service):
    """ Appends each inbound HL7 message to a file. Returns nothing, so the channel auto-ACKs with AA.
    """
    name = 'test.hl7.mllp.echo'

    def handle(self):

        # The MLLP channel delivers text while the REST channel delivers bytes
        message = self.request.raw_request
        if isinstance(message, bytes):
            message = message.decode('utf-8')

        with open(_messages_file, 'a') as file_handle:
            _ = file_handle.write(json.dumps(message) + '\\n')

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

accept_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class TestHL7MLLPAccept(Service):
    """ Accepts any input, parsed or raw, and does nothing - the channel auto-ACKs with AA.
    Used by the audit tests, which read the audit database instead of the service's output.
    """
    name = 'test.hl7.mllp.accept'

    def handle(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

fhir_invoke_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_outconn_name = 'test-fhir-audit-outconn'

# ################################################################################################################################
# ################################################################################################################################

class TestHL7FHIRInvoke(Service):
    """ Reads one Patient resource through the FHIR outconn, the same way user services do.
    """
    name = 'test.hl7.fhir.invoke'

    def handle(self):
        client = self.fhir[_outconn_name]
        _ = client.execute(path='Patient/example', method='get')

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

fhir_save_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_outconn_name = 'test-fhir-resend-outconn'

# ################################################################################################################################
# ################################################################################################################################

class TestHL7FHIRSave(Service):
    """ Writes one Patient resource through the FHIR outconn - the delivery
    the per-hop resend test repeats.
    """
    name = 'test.hl7.fhir.save'

    def handle(self):
        client = self.fhir[_outconn_name]
        _ = client.execute(
            path='Patient',
            method='post',
            data={'resourceType': 'Patient', 'name': [{'family': 'Kowalska', 'given': ['Maria']}]},
        )

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

alert_rule_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import Alerting
from zato.common.alerting.seed import alerts_ruleset
from zato.common.json_internal import dumps, loads
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Documents_Key
from zato.server.rule_engine_api import get_backend
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# Who the versions these services store are attributed to.
_actor = 'test.alerting'

# ################################################################################################################################

def _publish_documents(documents, comment):
    """ Stores the given rule documents as a new version of the alerts ruleset
    and makes that version live, returning the version number.
    """
    backend = get_backend()

    matches = backend.definitions.find_by_name(name=Alerting.Ruleset_Name, object_type=Definition_Type_Ruleset)
    definition = matches[0]

    record = backend.versions.create(
        definition_id=definition.id,
        expected_current_version=definition.current_version,
        document={Documents_Key: documents},
        author=_actor,
        comment=comment,
    )
    _ = backend.versions.publish(definition_id=definition.id, version=record.version, actor=_actor)

    return record.version

# ################################################################################################################################
# ################################################################################################################################

class TestAlertingRuleSave(Service):
    """ Replaces the alerts ruleset's live rules with the ones given as rules text,
    so the alerting sweep test runs against exactly the rules it configures.
    """
    name = 'test.alerting.rule.save'

    def handle(self):

        request = self.request.raw_request
        if isinstance(request, (str, bytes)):
            request = loads(request)

        text = request['text']

        documents, errors = parse_data_details(text, Alerting.Ruleset_Name)
        if errors:
            raise Exception('The test alert rules do not parse -> {}'.format(errors))

        version = _publish_documents(documents, 'Test alert rules')

        self.response.payload = dumps({'is_ok': True, 'version': version})

# ################################################################################################################################
# ################################################################################################################################

class TestAlertingRuleDelete(Service):
    """ Restores the seeded default alert rules, so the alerting test leaves
    no configuration behind for the other test modules.
    """
    name = 'test.alerting.rule.delete'

    def handle(self):

        document = alerts_ruleset()
        version = _publish_documents(document[Documents_Key], 'Restored default alert rules')

        self.response.payload = dumps({'is_ok': True, 'version': version})

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

demo_import_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.demo.seed import SeedConfig
from zato.common.json_internal import dumps, loads
from zato.server.demo import import_demo_data, remove_demo_data
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class TestDemoImport(Service):
    """ Runs the demo-data import on this server - the same plain function
    a dashboard view invokes, exercised here over a live environment.
    The request may size the run down, so the test stays fast.
    """
    name = 'test.demo.import'

    def handle(self):

        request = self.request.raw_request
        if isinstance(request, (str, bytes)):
            request = loads(request)

        config = SeedConfig()
        config.days = request['days']
        config.messages_per_day = request['messages_per_day']
        config.burst_message_count = request['burst_message_count']
        config.fhir_pair_count = request['fhir_pair_count']

        result = import_demo_data(self.server, config=config)
        self.response.payload = dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class TestDemoPurge(Service):
    """ Undoes the demo import through the same server-side function the
    dashboard's removal path uses, so this test module leaves nothing behind.
    """
    name = 'test.demo.purge'

    def handle(self):
        result = remove_demo_data(self.server)
        self.response.payload = dumps(result)

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

error_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class TestHL7MLLPError(Service):
    """ Always raises an exception so the channel returns AE ACK with an ERR segment.
    """
    name = 'test.hl7.mllp.error'

    def handle(self):
        raise Exception('Deliberate test error')

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

forward_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_outconn_name = 'test-mllp-wire-outconn'

# ################################################################################################################################
# ################################################################################################################################

class TestHL7MLLPForward(Service):
    """ Forwards the inbound HL7 message through the MLLP outconn to the standalone backend server.
    """
    name = 'test.hl7.mllp.forward'

    def handle(self):

        # Send the message through the outgoing connection, the same way user services do
        _ = self.mllp[_outconn_name].send(self.request.raw_request)

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

destination_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# The destinations of the channel this service runs on, by the names the channel declares them under
_forward_destination = 'forward-ehr'
_fhir_destination = 'fhir-ehr'

# ################################################################################################################################
# ################################################################################################################################

class TestHL7MLLPDestinations(Service):
    """ Says what each destination of its channel receives, in the way the message asks for -
    the tests send one message per way of saying it.
    """
    name = 'test.hl7.mllp.destinations'

    def handle(self):

        message = self.request.raw_request
        if isinstance(message, bytes):
            message = message.decode('utf-8')

        # A FHIR server is sent a resource rather than the HL7 message the channel received,
        # so this one destination is always spoken for
        self.destination[_fhir_destination] = {'resourceType': 'Patient', 'id': 'from-the-service'}

        # Every destination receives what the service made of the message ..
        if 'BROADCAST' in message:
            self.destination.payload = message + '\\rNTE|1||Seen by the service'

        # .. one destination receives something of its own ..
        elif 'PER_NAME' in message:
            self.destination[_forward_destination] = message + '\\rNTE|1||For the EHR alone'

        # .. and one destination receives nothing at all.
        elif 'DROPPED' in message:
            self.destination[_forward_destination] = None

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################

inspect_service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# The file where the echo service stores received messages, one JSON string per line
_messages_file = os.environ['Zato_Test_MLLP_Messages_File']

# ################################################################################################################################
# ################################################################################################################################

class TestHL7MLLPInspect(Service):
    """ Returns the list of messages captured by the echo service. Invoked via REST by tests.
    """
    name = 'test.hl7.mllp.inspect'

    def handle(self):

        messages = []

        # The file does not exist until the echo service receives its first message
        if os.path.exists(_messages_file):
            with open(_messages_file) as file_handle:
                for line in file_handle:
                    line = line.strip()
                    if line:
                        messages.append(json.loads(line))

        out = json.dumps({'messages': messages})
        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################
