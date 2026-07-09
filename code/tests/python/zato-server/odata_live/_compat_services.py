# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The services below re-create, with fully anonymized names and data, the logic of existing
production services built on RESTAdapter - they prove that RESTAdapter keeps working
unchanged next to the new OData client.
"""

# stdlib
import json
from dataclasses import dataclass
from hashlib import sha256

# Zato
from zato.common.marshal_.api import Model
from zato.server.service import RESTAdapter

# ################################################################################################################################
# ################################################################################################################################

# The code prefix percentage-style discount codes carry, e.g. PCT10 means ten percent.
Percentage_Prefix = 'PCT'

# What currency each posting group defaults to when a record does not carry one.
Domestic_Posting_Group = 'DOMESTIC'
Domestic_Currency = 'EUR'
Foreign_Currency = 'USD'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Discount(Model):
    key: 'str'
    company: 'str'
    code: 'str'
    percentage: 'float'
    currency: 'str'
    record_hash: 'str'

    def update_hash(self):
        source = f'{self.key}:{self.percentage}:{self.currency}'
        self.record_hash = sha256(source.encode('utf8')).hexdigest()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InvoiceRate(Model):
    key: 'str'
    company: 'str'
    currency_code: 'str'
    rate: 'float'
    starting_date: 'str'

# ################################################################################################################################
# ################################################################################################################################

class _BCLookupAdapter(RESTAdapter):
    """ The base lookup adapter - fills the {env}, {company} and optional {entry} path
    placeholders from the input payload and passes an optional $filter through.
    """
    input = 'env', 'company', '-entry', '-filter'

    def get_path_params(self, params):

        out = {
            'env': self.request.input.env,
            'company': self.request.input.company,
        }

        if self.request.input.entry:
            out['entry'] = self.request.input.entry

        return out

    def get_query_string(self, params):

        out = {}

        if self.request.input.filter:
            out['$filter'] = self.request.input.filter

        return out

# ################################################################################################################################
# ################################################################################################################################

class CompatGetDiscounts(_BCLookupAdapter):
    """ Maps a 'value' list into Discount models - blocked records are skipped, the
    percentage is parsed out of the prefixed code, the currency defaults based on
    the posting group and each model gets a composite business key and a hash.
    """
    name = 'test.compat.get-discounts'
    conn_name = 'test.compat.discounts'

    def map_response(self, data, **kwargs):

        company = self.request.input.company

        out = []

        for item in data['value']:

            # Records the source system blocked never make it into the output.
            if item['blocked']:
                continue

            discount = Discount()
            discount.company = company
            discount.code = item['code']

            # The percentage lives inside the prefixed code, e.g. PCT25 is 25 percent.
            discount.percentage = float(item['code'][len(Percentage_Prefix):])

            # The currency defaults based on the posting group when the record has none.
            currency = item['currency']
            if not currency:
                if item['postingGroup'] == Domestic_Posting_Group:
                    currency = Domestic_Currency
                else:
                    currency = Foreign_Currency
            discount.currency = currency

            # The business key is composite and the hash covers the mapped values.
            discount.key = f'{company}-{item["code"]}'
            discount.update_hash()

            out.append(discount.to_dict())

        return json.dumps({'items': out})

# ################################################################################################################################
# ################################################################################################################################

class CompatGetDiscountEntry(_BCLookupAdapter):
    """ Maps a single entry - the response is one object, not a 'value' list.
    """
    name = 'test.compat.get-discount-entry'
    conn_name = 'test.compat.discount-entry'

    def map_response(self, data, **kwargs):

        company = self.request.input.company

        discount = Discount()
        discount.company = company
        discount.code = data['code']
        discount.percentage = float(data['code'][len(Percentage_Prefix):])
        discount.currency = data['currency']
        discount.key = f'{company}-{data["code"]}'
        discount.update_hash()

        return json.dumps({'entry': discount.to_dict()})

# ################################################################################################################################
# ################################################################################################################################

class CompatGetInvoiceRates(_BCLookupAdapter):
    """ Exchange-rate style dedup - only the latest record per currency key by date
    is kept in the output.
    """
    name = 'test.compat.get-invoice-rates'
    conn_name = 'test.compat.invoice-rates'

    def map_response(self, data, **kwargs):

        company = self.request.input.company

        latest = {}

        for item in data['value']:

            rate = InvoiceRate()
            rate.company = company
            rate.currency_code = item['currencyCode']
            rate.rate = item['rate']
            rate.starting_date = item['startingDate']
            rate.key = f'{company}-{item["currencyCode"]}'

            # Keep only the latest record per key - the dates are ISO-formatted
            # so string comparison orders them correctly.
            current = latest.get(rate.key)
            if current is None or rate.starting_date > current.starting_date:
                latest[rate.key] = rate

        out = []
        for rate in latest.values():
            out.append(rate.to_dict())

        return json.dumps({'items': out})

# ################################################################################################################################
# ################################################################################################################################

class CompatCreateOrder(RESTAdapter):
    """ Creates an order - the request is a nested payload of order lines, each line
    optionally carrying dimension-like sub-lines, and the response maps to the number
    of the order the system created.
    """
    name = 'test.compat.create-order'
    conn_name = 'test.compat.orders'
    method = 'POST'

    input = 'env', 'company', 'number', 'customer_number', 'lines'

    def get_path_params(self, params):
        return {
            'env': self.request.input.env,
            'company': self.request.input.company,
        }

    def get_request(self):

        lines = []

        for line in self.request.input.lines:

            out_line = {
                'itemNumber': line['item_number'],
                'quantity': line['quantity'],
            }

            # Dimension-like sub-lines are optional per line.
            if 'dimensions' in line:
                out_dimensions = []
                for dimension in line['dimensions']:
                    out_dimensions.append({
                        'code': dimension['code'],
                        'value': dimension['value'],
                    })
                out_line['dimensions'] = out_dimensions

            lines.append(out_line)

        payload = {
            'number': self.request.input.number,
            'customerNumber': self.request.input.customer_number,
            'salesLines': lines,
        }

        return json.dumps(payload)

    def map_response(self, data, **kwargs):
        return json.dumps({'order_number': data['number']})

# ################################################################################################################################
# ################################################################################################################################

class CompatImportXML(RESTAdapter):
    """ Posts an XML document - the content type is application/xml, the SOAPAction
    header comes from the input and the body is passed through from the payload.
    """
    name = 'test.compat.import-xml'
    conn_name = 'test.compat.xml-import'
    method = 'POST'

    def get_path_params(self, params):
        payload = self.request.payload
        return {
            'env': payload['env'],
        }

    def get_headers(self):
        payload = self.request.payload
        return {
            'Content-Type': 'application/xml',
            'SOAPAction': payload['soap_action'],
        }

    def get_request(self):
        payload = self.request.payload
        return payload['body']

    def map_response(self, data, **kwargs):
        return json.dumps({'result': data})

# ################################################################################################################################
# ################################################################################################################################
