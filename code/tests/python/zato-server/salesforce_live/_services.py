# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from urllib.parse import quote

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class SalesforceTestCreateCampaign(Service):
    """ Creates a campaign through a named Salesforce connection.
    """
    name = 'test.salesforce.create-campaign'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        campaign_name = self.request.raw_request['campaign_name']
        segment = self.request.raw_request['segment']

        # The campaign to create ..
        request = {
            'Name': campaign_name,
            'Segment__c': segment,
        }

        # .. create it now ..
        conn = self.salesforce[conn_name]
        response = conn.post('/sobjects/Campaign/', request)

        # .. and return the new record's ID.
        campaign_id = response['id']
        self.response.payload = json.dumps({'campaign_id': campaign_id})

# ################################################################################################################################
# ################################################################################################################################

class SalesforceTestGetCampaign(Service):
    """ Reads a single campaign record through a named Salesforce connection.
    """
    name = 'test.salesforce.get-campaign'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        campaign_id = self.request.raw_request['campaign_id']

        # Read the record ..
        conn = self.salesforce[conn_name]
        response = conn.get(f'/sobjects/Campaign/{campaign_id}')

        # .. and return it as is.
        self.response.payload = json.dumps(response)

# ################################################################################################################################
# ################################################################################################################################

class SalesforceTestUpdateCampaign(Service):
    """ Updates selected fields of a campaign through a named Salesforce connection.
    """
    name = 'test.salesforce.update-campaign'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        campaign_id = self.request.raw_request['campaign_id']
        segment = self.request.raw_request['segment']

        # Only the fields that changed go into the request ..
        request = {
            'Segment__c': segment,
        }

        # .. send the partial update now - Salesforce answers with 204 No Content.
        conn = self.salesforce[conn_name]
        _ = conn.patch(f'/sobjects/Campaign/{campaign_id}', request)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class SalesforceTestDeleteCampaign(Service):
    """ Deletes a campaign through a named Salesforce connection.
    """
    name = 'test.salesforce.delete-campaign'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        campaign_id = self.request.raw_request['campaign_id']

        # Delete the record - Salesforce answers with 204 No Content.
        conn = self.salesforce[conn_name]
        _ = conn.delete(f'/sobjects/Campaign/{campaign_id}')

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class SalesforceTestUpsertCampaign(Service):
    """ Creates or updates a campaign by its external ID through a named Salesforce connection.
    """
    name = 'test.salesforce.upsert-campaign'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        external_id = self.request.raw_request['external_id']
        campaign_name = self.request.raw_request['campaign_name']

        # The fields to create the record with or to update it to ..
        request = {
            'Name': campaign_name,
        }

        # .. upsert by the external ID now - a create answers with the record's details,
        # .. an update with an empty response.
        conn = self.salesforce[conn_name]
        response = conn.patch(f'/sobjects/Campaign/Campaign_Code__c/{external_id}', request)

        self.response.payload = json.dumps({'response': response})

# ################################################################################################################################
# ################################################################################################################################

class SalesforceTestQueryCampaigns(Service):
    """ Runs a SOQL query through a named Salesforce connection.
    """
    name = 'test.salesforce.query-campaigns'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        # The query to run ..
        query = 'SELECT Id, Name, Segment__c FROM Campaign'
        query_path = '/query/?q=' + quote(query)

        # .. run it now ..
        conn = self.salesforce[conn_name]
        response = conn.get(query_path)

        page_records = response['records']
        records = list(page_records)

        # .. follow the pagination trail until Salesforce reports the result set is complete ..
        while not response['done']:
            next_records_url = response['nextRecordsUrl']
            response = conn.get(next_records_url)

            page_records = response['records']
            records.extend(page_records)

        # .. and return the records found.
        self.response.payload = json.dumps({'records': records})

# ################################################################################################################################
# ################################################################################################################################

class SalesforceTestPing(Service):
    """ Pings a named Salesforce connection.
    """
    name = 'test.salesforce.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        # A ping lists the resources of the API version the connection uses.
        conn = self.salesforce[conn_name]
        response = conn.ping()

        self.response.payload = json.dumps({'ok': True, 'resources': response})

# ################################################################################################################################
# ################################################################################################################################
