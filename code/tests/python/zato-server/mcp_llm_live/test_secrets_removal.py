# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# local
import _agent
import _constants
import _diag
import _helpers
from _helpers import call_and_read_event as _call_and_read_event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple

# ################################################################################################################################
# ################################################################################################################################

# The detector names the audit trace counts findings under
_detector_api_token   = 'secret_api_token'
_detector_aws_key     = 'secret_aws_access_key'
_detector_bearer      = 'secret_bearer'
_detector_conn_string = 'secret_connection_string'
_detector_jwt         = 'secret_jwt'
_detector_private_key = 'secret_private_key'

# What the record's fields read once their credential-shaped values are stable replacements -
# each string value is replaced on its own, so a lone value always gets the first number
# and the twice-written AWS key shares one number within its field.
_api_note_replaced  = 'The integration was provisioned with REPLACED_SECRET_API_TOKEN_1 last spring'
_aws_note_replaced  = 'Backups sign with REPLACED_SECRET_AWS_ACCESS_KEY_1, the standby job reuses REPLACED_SECRET_AWS_ACCESS_KEY_1 as well'
_session_replaced   = 'The portal session cookie carries REPLACED_SECRET_JWT_1'
_auth_note_replaced = 'Each call sends Authorization: REPLACED_SECRET_BEARER_1'
_db_note_replaced   = 'Reports read from REPLACED_SECRET_CONNECTION_STRING_1 nightly'
_deploy_key_replaced = 'REPLACED_SECRET_PRIVATE_KEY_1'

# The prefix every secrets replacement carries, for the wire sweeps
_secret_replacement_prefix = 'REPLACED_SECRET_'

# ################################################################################################################################
# ################################################################################################################################

def _get_customer_record(
    zato_server:'anydict',
    url_path:'str',
    gateway_name:'str',
    ) -> 'anytuple':
    """ One call for the secrets customer through the given gateway, returning the record
    and the audit data document of the call's event.
    """

    body, event_data = _call_and_read_event(
        zato_server, url_path, gateway_name,
        _constants.Service_Customer_Get, {'customer_id': _constants.Customer_ID_Secrets})

    data = _helpers.get_result_data(body)

    out = data, event_data
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSecretsRemoval:
    """ The secrets stage replaces credential-shaped values with stable replacements
    and the audit trace counts the findings per detector.
    """

# ################################################################################################################################

    def test_every_credential_shape_is_replaced_and_counted(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_Secrets, _constants.Gateway_Secrets)

        # Each field's credential-shaped value is a token now ..
        assert data['api_note'] == _api_note_replaced, data['api_note']
        assert data['session_note'] == _session_replaced, data['session_note']
        assert data['auth_note'] == _auth_note_replaced, data['auth_note']
        assert data['db_note'] == _db_note_replaced, data['db_note']
        assert data['deploy_key'] == _deploy_key_replaced, data['deploy_key']

        # .. no secret survives anywhere in the response ..
        data_text = str(data)

        for secret in _constants.Secret_Values:
            assert secret not in data_text, data_text

        # .. and the trace counts each detector's findings.
        assert event_data['secrets_removed'] == {
            _detector_api_token: 1,
            _detector_aws_key: 2,
            _detector_bearer: 1,
            _detector_conn_string: 1,
            _detector_jwt: 1,
            _detector_private_key: 1,
        }, event_data

# ################################################################################################################################

    def test_stable_replacements_repeat_for_the_same_value(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_Secrets, _constants.Gateway_Secrets)

        # The AWS key written twice in one field shares one numbered replacement
        assert data['aws_note'] == _aws_note_replaced, data['aws_note']
        assert event_data['secrets_removed'][_detector_aws_key] == 2, event_data

# ################################################################################################################################

    def test_ordinary_fields_survive_byte_identical(self, zato_server:'anydict') -> 'None':

        data, _event_data = _get_customer_record(
            zato_server, _constants.Path_Secrets, _constants.Gateway_Secrets)

        # The fields with no credential-shaped values in them are untouched to the byte
        assert data['name'] == _constants.Customer_Name_Secrets, data['name']
        assert data['city'] == _constants.Customer_City_Secrets, data['city']

# ################################################################################################################################

    def test_a_gateway_without_the_stage_passes_secrets_through(self, zato_server:'anydict') -> 'None':

        data, event_data = _get_customer_record(
            zato_server, _constants.Path_Main, _constants.Gateway_Main)

        # The plain gateway runs no secrets stage, so every value arrives as the service built it ..
        data_text = str(data)

        for secret in _constants.Secret_Values:
            assert secret in data_text, data_text

        # .. and no count was written.
        assert 'secrets_removed' not in event_data, event_data

# ################################################################################################################################
# ################################################################################################################################

class TestSecretsThroughModel:
    """ The model wire - every chat request and the final answer carry
    the stable replacements only, never a credential-shaped value.
    """

# ################################################################################################################################

    def test_replaced_secrets_are_all_the_model_ever_sees(self, zato_server:'anydict', ollama:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Secrets)

        task = 'Fetch the record of customer CRM-9001 and summarize the operational notes you received.'
        result = _agent.run_agent(client, task)

        # Every chat request the conversation sent carries replacements only ..
        chat_requests = _diag.get_entries('chat_request')
        assert chat_requests, 'No chat requests were logged'

        for entry in chat_requests:
            request_text = dumps(entry['payload'])

            for secret in _constants.Secret_Values:
                assert secret not in request_text, secret

        # .. at least one of them carries the replacements themselves ..
        all_requests_text = dumps(chat_requests)
        assert _secret_replacement_prefix in all_requests_text, all_requests_text

        # .. and the final answer is as free of the secrets as the requests were.
        for secret in _constants.Secret_Values:
            assert secret not in result.final_text, result.final_text

# ################################################################################################################################
# ################################################################################################################################
