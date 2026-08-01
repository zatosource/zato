# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# The file name the service is hot-deployed under
Service_File_Name = '_test_mllp_outconn_third_party.py'

# What a test invokes to send a message through an outgoing connection
Send_Service_Name = 'test.mllp.outconn.send'

# ################################################################################################################################
# ################################################################################################################################

# The one service this suite deploys. Every test sends through it rather than through a channel,
# because what is under test is the outgoing side on its own - a channel in front of it would only
# add a second set of framing rules and a second acknowledgment to tell apart from the first.
#
# The result is reported rather than raised, because a send that fails is as much of an answer as
# one that succeeds and a test has to be able to assert on either without the invocation itself
# turning into an error page.
service_source = '''\
# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic
from traceback import format_exc

# gevent
from gevent import joinall, spawn

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# How many milliseconds one second holds, the unit every duration reported here is expressed in
_Ms_Per_Second = 1000

# How many messages a request that does not say carries
_Default_Count = 1

# Where a control id of its own goes in the message each of a concurrent run is given
_Control_Id_Marker = '@control_id@'

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPOutconnSend(Service):
    """ Sends one message, or several at once, through a named MLLP outgoing connection and reports
    what came back from each of them.
    """
    name = 'test.mllp.outconn.send'

    def handle(self) -> 'None':

        request = self.request.raw_request

        outconn_name = request['outconn']
        data = request['data']

        # A test of what a pool does under load sends the same message several times at once, and
        # everything else sends it the once
        count = request.get('count', _Default_Count)

        # Each message of a concurrent run needs a control id of its own, so that a reply landing
        # at the wrong sender is something a test can see rather than something it cannot tell from
        # a reply landing at the right one
        control_ids = request.get('control_ids', [])

        greenlets = []

        for index in range(count):

            if control_ids:
                message = data.replace(_Control_Id_Marker, control_ids[index])
            else:
                message = data

            greenlets.append(spawn(self._send_one, outconn_name, message))

        _ = joinall(greenlets)

        results = []

        for greenlet in greenlets:
            results.append(greenlet.value)

        self.response.payload = {'results': results}

# ################################################################################################################################

    def _send_one(self, outconn_name:'str', data:'str') -> 'stranydict':
        """ Sends one message and returns everything about how it went that a test may assert on.
        """
        start = monotonic()

        try:
            ack = self.mllp[outconn_name].send(data)
        except Exception:

            # A send that raised never got an acknowledgment at all, which is a different outcome
            # from one that got a negative acknowledgment back
            elapsed_ms = int((monotonic() - start) * _Ms_Per_Second)

            out = {
                'is_sent': False,
                'ack_code': '',
                'is_accepted': False,
                'should_retry': False,
                'error_text': format_exc(),
                'ack_text': '',
                'elapsed_ms': elapsed_ms,
            }

            return out

        elapsed_ms = int((monotonic() - start) * _Ms_Per_Second)

        out = {
            'is_sent': True,
            'ack_code': ack.ack_code,
            'is_accepted': ack.is_accepted,
            'should_retry': ack.should_retry,
            'error_text': ack.error_text,
            'ack_text': ack.ack_text,
            'elapsed_ms': elapsed_ms,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################
'''

# ################################################################################################################################
# ################################################################################################################################
