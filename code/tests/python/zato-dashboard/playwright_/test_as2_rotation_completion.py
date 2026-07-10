# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# Zato
from zato.common.api import AS2
from zato.common.crypto.api import CryptoManager
from zato.common.defaults import default_cluster_id
from zato.common.test.playwright_pubsub import close_dialog_via_jquery
from as2_outconn import create_as2_outconn, delete_as2_outconn, open_as2_outconn_page, open_edit_dialog, \
    wait_for_as2_outconn_row
from as4_keys import new_test_parties

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict
    from client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as2.rotation.' + CryptoManager.generate_hex_string(32) + '.'

# How many days before today the backdated activation date lies - well past the one-day grace window.
_Backdated_Days = 3

# An activation date that will not arrive during any test run.
_Future_Date = '2099-01-01'

# ################################################################################################################################
# ################################################################################################################################

def _backdated_activation_date() -> 'str':
    """ An activation date far enough in the past for the rotation to be ready for completion.
    """
    now = datetime.now(timezone.utc)
    activation = now - timedelta(days=_Backdated_Days)

    out = activation.strftime('%Y-%m-%d')
    return out

# ################################################################################################################################

def _new_connection_options(current_cert:'str', next_cert:'str', next_cert_from:'str', key_material:'anydict') -> 'anydict':
    """ The create form options of one test connection - the identities and key material
    plus the certificate rotation fields under test.
    """
    out = {
        'as2_from': 'ZatoRetail',
        'as2_to': 'PartnerCorp',
        'as2_partner_cert': current_cert,
        'as2_partner_next_cert': next_cert,
    }

    if next_cert_from:
        out['as2_partner_next_cert_from'] = next_cert_from

    out.update(key_material)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAS2RotationCompletion:
    """ The automatic completion of staged certificate rotations - a backdated activation date
    makes the sweep service promote the next certificate to the current one in the stored config,
    while future-dated and dateless next certificates stay untouched.
    """

# ################################################################################################################################

    def test_sweep_completes_backdated_rotation_only(
        self, logged_in_page:'Page', zato_dashboard:'anydict', api_client:'ZatoClient') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        sender, receiver = new_test_parties()
        _, next_party = new_test_parties()

        current_cert = receiver.certificate
        next_cert = next_party.certificate

        # Our own key material, shared by all three connections.
        key_material = {
            'as2_signing_key': sender.key,
            'as2_signing_cert_chain': sender.certificate,
            'as2_decryption_key': sender.key,
        }

        backdated_name = _Test_Name_Prefix + 'backdated'
        future_name = _Test_Name_Prefix + 'future'
        dateless_name = _Test_Name_Prefix + 'dateless'

        # Create a connection whose activation date lies beyond the grace window ..
        backdated_options = _new_connection_options(current_cert, next_cert, _backdated_activation_date(), key_material)
        backdated_id = create_as2_outconn(page, base_url, backdated_name, 'https://as2.example.com/exchange',
            backdated_options)

        # .. one whose activation date has not arrived yet ..
        future_options = _new_connection_options(current_cert, next_cert, _Future_Date, key_material)
        future_id = create_as2_outconn(page, base_url, future_name, 'https://as2.example.com/exchange', future_options)

        # .. and one whose next certificate has no date at all.
        dateless_options = _new_connection_options(current_cert, next_cert, '', key_material)
        dateless_id = create_as2_outconn(page, base_url, dateless_name, 'https://as2.example.com/exchange', dateless_options)

        # Run the sweep - the scheduler is what invokes it in production, while the quickstart
        # environment under test runs with no scheduler process, so it is invoked directly here.
        _ = api_client.invoke(AS2.Default.Rotation_Service)

        # Reload so the table is rebuilt from what the server now has stored ..
        open_as2_outconn_page(page, base_url, query=backdated_name)
        _ = wait_for_as2_outconn_row(page, backdated_name)

        # .. the backdated connection's rotation is completed - the ex-next certificate
        # is the current one and both next-certificate fields are empty ..
        open_edit_dialog(page, backdated_id)

        assert page.input_value('#id_edit-as2_partner_cert').strip() == next_cert.strip()
        assert page.input_value('#id_edit-as2_partner_next_cert') == ''
        assert page.input_value('#id_edit-as2_partner_next_cert_from') == ''

        close_dialog_via_jquery(page, 'edit-div')

        # .. the future-dated connection is untouched ..
        open_as2_outconn_page(page, base_url, query=future_name)
        _ = wait_for_as2_outconn_row(page, future_name)
        open_edit_dialog(page, future_id)

        assert page.input_value('#id_edit-as2_partner_cert').strip() == current_cert.strip()
        assert page.input_value('#id_edit-as2_partner_next_cert').strip() == next_cert.strip()
        assert page.input_value('#id_edit-as2_partner_next_cert_from') == _Future_Date

        close_dialog_via_jquery(page, 'edit-div')

        # .. and so is the one with no activation date.
        open_as2_outconn_page(page, base_url, query=dateless_name)
        _ = wait_for_as2_outconn_row(page, dateless_name)
        open_edit_dialog(page, dateless_id)

        assert page.input_value('#id_edit-as2_partner_cert').strip() == current_cert.strip()
        assert page.input_value('#id_edit-as2_partner_next_cert').strip() == next_cert.strip()
        assert page.input_value('#id_edit-as2_partner_next_cert_from') == ''

        close_dialog_via_jquery(page, 'edit-div')

        # Clean up - the delete call needs the connection's row in the table,
        # so the page is reopened with each connection's name first.
        open_as2_outconn_page(page, base_url, query=backdated_name)
        _ = wait_for_as2_outconn_row(page, backdated_name)
        delete_as2_outconn(page, backdated_id)

        open_as2_outconn_page(page, base_url, query=future_name)
        _ = wait_for_as2_outconn_row(page, future_name)
        delete_as2_outconn(page, future_id)

        open_as2_outconn_page(page, base_url, query=dateless_name)
        _ = wait_for_as2_outconn_row(page, dateless_name)
        delete_as2_outconn(page, dateless_id)

# ################################################################################################################################

    def test_rotation_completion_job_exists(self, logged_in_page:'Page', api_client:'ZatoClient') -> 'None':
        """ Server startup creates the interval job that runs the sweep in production.
        """
        jobs, _ = api_client.get_list('zato.scheduler.job.get-list', cluster_id=default_cluster_id)

        job_names = []
        for job in jobs:
            job_names.append(job['name'])

        assert AS2.Default.Rotation_Job_Name in job_names

# ################################################################################################################################
# ################################################################################################################################
