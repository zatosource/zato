# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from email.parser import Parser
from typing import NamedTuple

# aiosmtpd
from aiosmtpd.controller import Controller

# Zato
from hl7_client.ports import find_free_port
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist
    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# What every listener here binds to
_Host = '127.0.0.1'

# What the SMTP protocol answers a delivery it accepted with
_Accepted = '250 OK'

# What the receiver keeps its messages in
email_list = list['ReceivedEmail']

# ################################################################################################################################
# ################################################################################################################################

class ReceivedEmail(NamedTuple):
    """ One e-mail as this receiver saw it.
    """
    sender: 'str'
    recipients: 'strlist'
    subject: 'str'
    body: 'str'
    arrived_at: 'float'

# ################################################################################################################################
# ################################################################################################################################

class _CollectingHandler:
    """ What aiosmtpd hands each delivered message to.
    """

    def __init__(self, receiver:'SMTPReceiver') -> 'None':
        self.receiver = receiver

    async def handle_DATA(self, server:'any_', session:'any_', envelope:'any_') -> 'str':

        content = envelope.content.decode('utf-8')
        parsed = Parser().parsestr(content)

        subject = parsed['Subject']
        if subject is None:
            subject = ''

        # A message an e-mail destination sends is a single-part one whose payload arrives
        # transfer-encoded (base64), which decode=True undoes, leaving the original bytes.
        body_bytes = cast_('bytes', parsed.get_payload(decode=True))
        body = body_bytes.decode('utf-8')

        message = ReceivedEmail(
            envelope.mail_from,
            list(envelope.rcpt_tos),
            subject,
            body,
            time.monotonic(),
        )
        self.receiver.messages.append(message)

        return _Accepted

# ################################################################################################################################
# ################################################################################################################################

class SMTPReceiver:
    """ The standard test SMTP server, aiosmtpd, recording every message delivered to it -
    what an e-mail destination sends is read back from here.
    """

    def __init__(self) -> 'None':
        self.port = find_free_port()
        self.messages:'email_list' = []

        self._controller:'any_' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the receiver on its port, which stays the same across a stop and a start.
        """
        handler = _CollectingHandler(self)

        self._controller = Controller(handler, hostname=_Host, port=self.port)
        self._controller.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the receiver, leaving its port free for a later start.
        """
        self._controller.stop()
        self._controller = None

# ################################################################################################################################
# ################################################################################################################################
