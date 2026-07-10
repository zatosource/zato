# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.common.as2.outbound import describe_send_result, new_send_report
from zato.common.json_internal import dumps
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

# What travels in the test message - the CID makes each test payload identifiable
# in logs and in the partner's system.
_test_message_template = 'This is a Zato AS2 test message; cid:{}'

# The filename the test payload travels under.
_test_message_filename = 'zato-as2-test-message.txt'

# ################################################################################################################################
# ################################################################################################################################

class SendTestMessage(AdminService):
    """ Sends a small identified test message through an outgoing AS2 connection
    and reports the MDN outcome - the certificate-and-connectivity check
    both sides perform during onboarding.
    """
    name = 'zato.outgoing.as2.send-test-message'
    input = 'name'
    output = 'response_data'

    def handle(self) -> 'None':

        name = self.request.input.name
        payload = _test_message_template.format(self.cid)

        # Send the payload through the real pipeline - a failed delivery comes back
        # as a report too, never as a bare exception, so the caller always sees
        # the same shape with the details inside.
        try:
            result = self.as2[name].send(payload, _test_message_filename)
            report = describe_send_result(result)
        except Exception:
            report = new_send_report()
            report['error'] = format_exc()

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################
