# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# The environment variable naming the directory the confirmation service keeps its attempt counters in
_marker_dir_env_key = 'Zato_Test_LLM_Marker_Dir'

# What the reference service answers for the capital question - deliberately not the real answer
_capital_answer = 'Perth'

# The format a report is built in when the caller names none
_default_format = 'summary'

# How long the slow echo sleeps, in seconds
_slow_seconds = 2

# How many spaces pad each text block - they collapse to one space under compaction
_pad_width = 400

# A base64 blob long enough for the base64 stripping stage to recognize it as one
_attachment_blob = 'data:image/png;base64,' + 'QUJDREVG' * 40

# What a confirmation reports on its first attempt, before the fulfilment system is reachable
_message_fulfilment_unavailable = 'Fulfilment system temporarily unavailable, try again'

# ################################################################################################################################
# ################################################################################################################################

class FactGet(Service):
    """ Answers general knowledge questions from the CRM reference base - pass the question to look up.
    """

    name = 'crm.fact.get'
    input = 'question'

    def handle(self):

        question = self.request.input.question

        self.response.payload = {
            'question': question,
            'answer': _capital_answer,
        }

# ################################################################################################################################
# ################################################################################################################################

class AccountLookup(Service):
    """ Returns the loyalty points balance of a customer account.
    """

    name = 'crm.account.lookup'
    input = 'customer_id'

    def handle(self):

        self.response.payload = {
            'customer_id': self.request.input.customer_id,
            'points': 4180,
        }

# ################################################################################################################################
# ################################################################################################################################

class AccountQuery(Service):
    """ Returns the outstanding debt of a customer account.
    """

    name = 'crm.account.query'
    input = 'customer_id'

    def handle(self):

        self.response.payload = {
            'customer_id': self.request.input.customer_id,
            'debt': 250,
        }

# ################################################################################################################################
# ################################################################################################################################

class EchoSlow(Service):
    """ Echoes a message back once the CRM read replica catches up - pass the message to echo.
    """

    name = 'crm.echo.slow'
    input = 'message'

    def handle(self):

        time.sleep(_slow_seconds)

        self.response.payload = {
            'echo': self.request.input.message,
        }

# ################################################################################################################################
# ################################################################################################################################

class OrderConfirm(Service):
    """ Confirms an order in the fulfilment system - pass the order id to confirm.
    """

    name = 'crm.order.confirm'
    input = 'order_id'

    def handle(self):

        order_id = self.request.input.order_id

        # Each order counts its attempts in a file of its own,
        # so the first attempt can fail and every later one succeed.
        marker_dir = os.environ[_marker_dir_env_key]
        counter_path = os.path.join(marker_dir, f'confirm.{order_id}.txt')

        if os.path.isfile(counter_path):
            with open(counter_path) as counter_file:
                counter_text = counter_file.read()
            attempt = int(counter_text)
        else:
            attempt = 0

        attempt += 1

        with open(counter_path, 'w') as counter_file:
            _ = counter_file.write(str(attempt))

        if attempt == 1:
            raise Exception(_message_fulfilment_unavailable)

        self.response.payload = {
            'order_id': order_id,
            'status': 'confirmed',
            'attempt': attempt,
        }

# ################################################################################################################################
# ################################################################################################################################

class TextPad(Service):
    """ Returns formatted text blocks of the CRM style guide - pass how many blocks to return.
    """

    name = 'crm.text.pad'
    input = 'count'

    def handle(self):

        count = int(self.request.input.count)

        padding = ' ' * _pad_width

        blocks = []

        for index in range(count):
            number = index + 1
            blocks.append({
                'block_id': number,
                'text': f'edge{padding}end',
            })

        self.response.payload = {'count': count, 'blocks': blocks}

# ################################################################################################################################
# ################################################################################################################################

class CustomerList(Service):
    """ Lists CRM customer records - pass how many to return.
    """

    name = 'crm.customer.list'
    input = 'count'

    def handle(self):

        count = int(self.request.input.count)

        customers = []

        for index in range(count):
            number = index + 1
            customers.append({
                'customer_id': f'CRM-9{number:04d}',
                'email': f'user{number}@example.com',
                'fax': None,
                'note': 'Priority    review  pending',
            })

        # The roster note carries markup and URLs on and off the allow list,
        # the attachment is a base64 blob - one response exercises every stage.
        self.response.payload = {
            'count': count,
            'roster_note': (
                '<script>showBanner()</script> quarterly  roster   list '
                'see https://example.com/kb and https://tracking.invalid/kb'),
            'attachment': _attachment_blob,
            'customers': customers,
        }

# ################################################################################################################################
# ################################################################################################################################

class ReportBuild(Service):
    """ Builds a customer report - pass the customer id and optionally the format to use.
    """

    name = 'crm.report.build'
    input = 'customer_id', '-format'

    def handle(self):

        report_format = self.request.input.format or _default_format

        self.response.payload = {
            'customer_id': self.request.input.customer_id,
            'format': report_format,
        }

# ################################################################################################################################
# ################################################################################################################################
