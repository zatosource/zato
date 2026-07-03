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

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_received_messages = []

# ################################################################################################################################
# ################################################################################################################################

class TestHL7MLLPEcho(Service):
    """ Stores each inbound HL7 message in a module-level list. Returns nothing, so the channel auto-ACKs with AA.
    """
    name = 'test.hl7.mllp.echo'

    def handle(self):
        _received_messages.append(self.request.raw_request)

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

        # Get the outconn wrapper from the config manager ..
        outconn_entry = self.server.config_manager.outconn_hl7_mllp[_outconn_name]
        wrapper = outconn_entry.conn

        # .. get a connection from the pool and send the message ..
        with wrapper.client() as connection:
            connection.invoke(self.request.raw_request)

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

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class TestHL7MLLPInspect(Service):
    """ Returns the list of messages captured by the echo service. Invoked via REST by tests.
    """
    name = 'test.hl7.mllp.inspect'

    def handle(self):

        # Import the echo service module to access its captured messages ..
        from _test_hl7_mllp_echo import _received_messages

        out = json.dumps({'messages': list(_received_messages)})
        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################
