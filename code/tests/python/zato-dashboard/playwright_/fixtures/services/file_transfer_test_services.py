# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from decimal import Decimal
from json import dumps

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# Every invoice the service processes is appended to this file - tests identify their own invoices by file name.
Invoice_Totals_Path = '/tmp/zato-test-file-transfer-invoice-totals.jsonl'

# ################################################################################################################################
# ################################################################################################################################

class InvoiceTotals(Service):
    """ The target service of the file transfer schedule tests - adds up the amounts of each invoice
    a schedule picks up and appends the result to a file that the tests read back.
    """

    name = 'test.file-transfer.invoice-totals'

    def handle(self):

        item = self.request.input

        # The invoice is a header line followed by one row per amount, the amount being the last column ..
        rows = item.text.splitlines()
        amount_rows = rows[1:]

        # .. the amounts are added up ..
        total = Decimal('0')

        for row in amount_rows:
            _, _, amount = row.rpartition(',')
            total += Decimal(amount)

        # .. and the result goes to the file the tests read.
        row_count = len(amount_rows)

        result = {
            'file_name': item.file_name,
            'conn_name': item.conn_name,
            'schedule_name': item.schedule_name,
            'row_count': row_count,
            'total': str(total),
        }

        line = dumps(result)
        line += '\n'

        with open(Invoice_Totals_Path, 'a') as totals_file:
            _ = totals_file.write(line)

        self.logger.info('Invoice `%s` from `%s` processed, total %s', item.file_name, item.conn_name, total)

# ################################################################################################################################
# ################################################################################################################################
