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
