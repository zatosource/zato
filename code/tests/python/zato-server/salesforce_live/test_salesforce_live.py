# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sys
from base64 import b64encode
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# Local
from _salesforce_server import SalesforceTestHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.salesforce_live')

# The main connection with valid credentials
_conn_name = 'test.salesforce.main'

# The connection whose password the token endpoint rejects
_bad_credentials_conn_name = 'test.salesforce.bad-credentials'

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Minimal admin client for invoking Zato services.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self.password = password

# ################################################################################################################################

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':

        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode()

        credentials = f'admin.invoke:{self.password}'
        auth = b64encode(credentials.encode()).decode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestSalesforceCampaigns:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        out = _AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        return out

# ################################################################################################################################

    def test_create_campaign(self, zato_server:'anydict') -> 'None':
        """ A campaign created through the connection arrives at the instance with its fields intact.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.salesforce.create-campaign', {
            'conn_name': _conn_name,
            'campaign_name': 'Summer promotion 2026',
            'segment': 'Enterprise customers',
        })

        campaign_id = result['campaign_id']
        assert campaign_id

        # The record arrived at the instance with its fields intact.
        campaign = SalesforceTestHandler.campaigns[campaign_id]

        assert campaign['Name'] == 'Summer promotion 2026'
        assert campaign['Segment__c'] == 'Enterprise customers'

# ################################################################################################################################

    def test_get_campaign(self, zato_server:'anydict') -> 'None':
        """ A single campaign record can be read back by its ID.
        """
        client = self._get_client(zato_server)

        created = client.invoke('test.salesforce.create-campaign', {
            'conn_name': _conn_name,
            'campaign_name': 'Renewal reminders',
            'segment': 'Existing subscribers',
        })

        campaign_id = created['campaign_id']

        result = client.invoke('test.salesforce.get-campaign', {
            'conn_name': _conn_name,
            'campaign_id': campaign_id,
        })

        assert result['Id'] == campaign_id
        assert result['Name'] == 'Renewal reminders'
        assert result['Segment__c'] == 'Existing subscribers'

# ################################################################################################################################

    def test_update_campaign(self, zato_server:'anydict') -> 'None':
        """ A partial update changes only the fields the request carries.
        """
        client = self._get_client(zato_server)

        created = client.invoke('test.salesforce.create-campaign', {
            'conn_name': _conn_name,
            'campaign_name': 'Quarterly newsletter',
            'segment': 'All subscribers',
        })

        campaign_id = created['campaign_id']

        _ = client.invoke('test.salesforce.update-campaign', {
            'conn_name': _conn_name,
            'campaign_id': campaign_id,
            'segment': 'Premium subscribers',
        })

        # The updated field changed and the rest of the record is intact.
        campaign = SalesforceTestHandler.campaigns[campaign_id]

        assert campaign['Segment__c'] == 'Premium subscribers'
        assert campaign['Name'] == 'Quarterly newsletter'

# ################################################################################################################################

    def test_delete_campaign(self, zato_server:'anydict') -> 'None':
        """ A deleted campaign is gone from the instance.
        """
        client = self._get_client(zato_server)

        created = client.invoke('test.salesforce.create-campaign', {
            'conn_name': _conn_name,
            'campaign_name': 'Obsolete promotion',
            'segment': 'Former customers',
        })

        campaign_id = created['campaign_id']

        _ = client.invoke('test.salesforce.delete-campaign', {
            'conn_name': _conn_name,
            'campaign_id': campaign_id,
        })

        assert campaign_id not in SalesforceTestHandler.campaigns

# ################################################################################################################################

    def test_upsert_campaign(self, zato_server:'anydict') -> 'None':
        """ An upsert by external ID creates the record first and updates it the second time.
        """
        client = self._get_client(zato_server)

        # The first upsert creates the record ..
        created = client.invoke('test.salesforce.upsert-campaign', {
            'conn_name': _conn_name,
            'external_id': 'CAMP-2026-001',
            'campaign_name': 'Partner day 2026',
        })

        response = created['response']
        campaign_id = response['id']

        assert response['created'] is True

        # .. and the second one updates it in place without creating a duplicate.
        updated = client.invoke('test.salesforce.upsert-campaign', {
            'conn_name': _conn_name,
            'external_id': 'CAMP-2026-001',
            'campaign_name': 'Partner day 2026 - rescheduled',
        })

        assert updated['response'] == {}

        campaign = SalesforceTestHandler.campaigns[campaign_id]

        assert campaign['Name'] == 'Partner day 2026 - rescheduled'
        assert campaign['Campaign_Code__c'] == 'CAMP-2026-001'

# ################################################################################################################################

    def test_query_campaigns(self, zato_server:'anydict') -> 'None':
        """ A SOQL query returns the records the instance holds, across all result pages.
        """
        client = self._get_client(zato_server)

        created = client.invoke('test.salesforce.create-campaign', {
            'conn_name': _conn_name,
            'campaign_name': 'Product launch webinar',
            'segment': 'Trial users',
        })

        campaign_id = created['campaign_id']

        result = client.invoke('test.salesforce.query-campaigns', {
            'conn_name': _conn_name,
        })

        records = result['records']

        ids = []
        for record in records:
            ids.append(record['Id'])

        assert campaign_id in ids

        # The instance answers queries in pages, so a full result set is larger than one page.
        record_count = len(records)
        page_size = SalesforceTestHandler.query_page_size

        assert record_count > page_size

# ################################################################################################################################
# ################################################################################################################################

class TestSalesforcePing:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        out = _AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        return out

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ .ping() succeeds against the live instance and returns its resource listing.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.salesforce.ping', {
            'conn_name': _conn_name,
        })

        assert result['ok'] is True
        assert 'sobjects' in result['resources']

# ################################################################################################################################
# ################################################################################################################################

class TestSalesforceSecurity:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        out = _AdminClient(zato_server['base_url'], zato_server['invoke_password'])
        return out

# ################################################################################################################################

    def test_bad_credentials_are_rejected(self, zato_server:'anydict') -> 'None':
        """ A connection with an invalid password cannot obtain an access token.
        """
        client = self._get_client(zato_server)

        with pytest.raises(Exception) as exception_info:
            _ = client.invoke('test.salesforce.ping', {
                'conn_name': _bad_credentials_conn_name,
            })

        assert 'HTTP' in str(exception_info.value)

# ################################################################################################################################

    def test_token_is_obtained_per_request(self, zato_server:'anydict') -> 'None':
        """ Every request first obtains an access token of its own from the token endpoint.
        """
        client = self._get_client(zato_server)

        _ = client.invoke('test.salesforce.ping', {
            'conn_name': _conn_name,
        })

        token_count_before = SalesforceTestHandler.issued_token_count

        _ = client.invoke('test.salesforce.ping', {
            'conn_name': _conn_name,
        })

        token_count_after = SalesforceTestHandler.issued_token_count
        assert token_count_after > token_count_before

# ################################################################################################################################
# ################################################################################################################################
