# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Zato
from zato.common.test.playwright_pubsub import open_create_dialog
from as4_channel import fill_as4_channel_form, open_as4_channel_page
from as4_outconn import fill_as4_outconn_form, open_as4_outconn_page
from soap_channel import fill_soap_channel_form, open_soap_channel_page
from soap_outconn import fill_soap_outconn_form, open_soap_outconn_page
from wss_definition import fill_wss_form, open_wss_page

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# Where the Dashboard screenshots for the documentation go - the whole module
# is skipped unless this points to a directory, so regular test runs never enter it.
_Screenshots_Dir = os.environ.get('Zato_Docs_Screenshots_Dir', '')

pytestmark = pytest.mark.skipif(not _Screenshots_Dir, reason='Zato_Docs_Screenshots_Dir is not set')

# The dialogs render at this size so tall tabs fit in one element screenshot
_Viewport = {'width': 1500, 'height': 1400}

# Example PEM material for the crypto fields - what a reader's own key looks like
_Pem_Key = (
    '-----BEGIN PRIVATE KEY-----\n'
    'MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7VJTUt9Us8cKj\n'
    'MzEfYyjiWA4R4/M2bS1GB4t7NXp98C3SC6dVMvDuictGeurT8jNbvJZHtCSuYEvu\n'
    '-----END PRIVATE KEY-----'
)

_Pem_Certificate = (
    '-----BEGIN CERTIFICATE-----\n'
    'MIIDdzCCAl+gAwIBAgIEbGRkYzANBgkqhkiG9w0BAQsFADBsMRAwDgYDVQQGEwdV\n'
    'bmtub3duMRAwDgYDVQQIEwdVbmtub3duMRAwDgYDVQQHEwdVbmtub3duMRAwDgYD\n'
    '-----END CERTIFICATE-----'
)

# ################################################################################################################################
# ################################################################################################################################

def _activate_create_tab(page:'Page', tab_name:'str') -> 'None':
    """ Clicks a tab header in the create dialog so the tab's fields become visible.
    """
    page.click(f'#create-div .dashboard-tab[data-tab="{tab_name}"]')

# ################################################################################################################################

def _screenshot(page:'Page', file_name:'str') -> 'None':
    """ Saves an element screenshot of the create dialog under the given name.
    """

    element = page.wait_for_selector('#create-div', state='visible', timeout=5000)

    path = os.path.join(_Screenshots_Dir, file_name + '.png')
    _ = element.screenshot(path=path)

# ################################################################################################################################

def _close_create_dialog(page:'Page') -> 'None':
    """ Closes the create dialog through its Cancel button.
    """

    page.click('#create-div button:has-text("Cancel")')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=5000)

# ################################################################################################################################

def _inject_service_option(page:'Page', service_name:'str') -> 'None':
    """ Adds a service name to the create form's service select and picks it -
    the dialog is only photographed, never submitted, so the option's presence
    in this particular environment does not matter.
    """

    page.evaluate(
        f'var select = $("#id_service");'
        f'select.append(new Option("{service_name}", "{service_name}"));'
        f'select.val("{service_name}").trigger("chosen:updated").trigger("change");'
    )

# ################################################################################################################################
# ################################################################################################################################

class TestDocsScreenshots:
    """ Produces the Dashboard screenshots the SOAP mandates pages embed. Each screenshot
    is a create dialog filled in the way the corresponding page describes.
    """

# ################################################################################################################################

    def test_generate_mandate_screenshots(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        page.set_viewport_size(_Viewport)

        #
        # healthcare-ihe - a WS-Security definition in SAML mode, photographed on its SAML tab
        #
        open_wss_page(page, base_url)
        open_create_dialog(page)

        fill_wss_form(page, {
            'name': 'Document Exchange',
            'mode': 'saml',
            'issuer': 'https://idp.example-hospital.org',
            'subject': 'CN=Dr. Jane Smith, O=General Hospital',
            'audience': 'https://gateway.example-hin.gov',
            'sign': True,
            'signing_key': _Pem_Key,
            'signing_certificate_chain': _Pem_Certificate,
        })

        _activate_create_tab(page, 'saml')
        _screenshot(page, 'ihe-saml-definition')
        _close_create_dialog(page)

        #
        # norway-helsenett - a WS-Security definition with the full crypto material,
        # photographed on its Crypto material tab
        #
        open_wss_page(page, base_url)
        open_create_dialog(page)

        fill_wss_form(page, {
            'name': 'Helsenett partner',
            'mode': 'x509',
            'sign': True,
            'encrypt': True,
            'signing_key': _Pem_Key,
            'signing_certificate_chain': _Pem_Certificate,
            'decryption_key': _Pem_Key,
            'peer_certificate': _Pem_Certificate,
            'trust_anchors': _Pem_Certificate,
        })

        _activate_create_tab(page, 'crypto')
        _screenshot(page, 'norway-crypto-tab')
        _close_create_dialog(page)

        #
        # healthcare-ihe - an outgoing connection with SOAP 1.2, WS-Addressing and MTOM,
        # photographed on its SOAP tab
        #
        open_soap_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_soap_outconn_form(page, {
            'name': 'Document Exchange',
            'host': 'https://gateway.example-hin.gov:443',
            'url_path': '/xdsb/repository',
            'soap_action': 'urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b',
            'soap_version': '1.2',
            'use_ws_addressing': True,
            'use_mtom': True,
        })

        _activate_create_tab(page, 'soap')
        _screenshot(page, 'ihe-soap-tab')
        _close_create_dialog(page)

        #
        # cdc-iis - an outgoing connection with SOAP 1.2 and the body-credential rows,
        # photographed on its SOAP tab and then on its Body credentials tab
        #
        open_soap_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_soap_outconn_form(page, {
            'name': 'State Registry',
            'host': 'https://iis.state.example.gov',
            'url_path': '/iis-service',
            'soap_action': 'urn:cdc:iisb:2014:submitSingleMessage',
            'soap_version': '1.2',
            'body_credentials': [
                {'name': 'username'},
                {'name': 'password'},
            ],
        })

        _activate_create_tab(page, 'soap')
        _screenshot(page, 'cdc-iis-soap-tab')

        _activate_create_tab(page, 'credentials')
        _screenshot(page, 'cdc-iis-body-credentials')
        _close_create_dialog(page)

        #
        # nhs-spine - an outgoing connection with the client certificate paths,
        # photographed on its Security tab
        #
        open_soap_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_soap_outconn_form(page, {
            'name': 'NHS Spine',
            'host': 'https://msg.spine.nhs.uk',
            'url_path': '/reliablemessaging/forwardreliable',
            'tls_client_cert': '/opt/zato/tls/spine-client-cert.pem',
            'tls_client_key': '/opt/zato/tls/spine-client-key.pem',
        })

        _activate_create_tab(page, 'security')
        _screenshot(page, 'nhs-security-tab')
        _close_create_dialog(page)

        #
        # healthcare-ihe - a channel with SOAP 1.2 and MTOM responses, photographed whole
        #
        open_soap_channel_page(page, base_url)
        open_create_dialog(page)

        _inject_service_option(page, 'document.repository.store')

        fill_soap_channel_form(page, {
            'name': 'Document Repository',
            'url_path': '/xdsb/repository',
            'service': 'document.repository.store',
            'soap_action': 'urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b',
            'soap_version': '1.2',
            'use_mtom': True,
        })

        _screenshot(page, 'ihe-channel')
        _close_create_dialog(page)

# ################################################################################################################################

    def test_generate_as4_screenshots(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        page.set_viewport_size(_Viewport)

        #
        # An outgoing Peppol connection - the access-point sender - photographed
        # on its Main tab, its Delivery tab with the discovery toggle and SML domain,
        # and its Security tab with the pasted-PEM keystore
        #
        open_as4_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_as4_outconn_form(page, {
            'name': 'Peppol Test Network',
            'as4_profile': 'peppol',
            'as4_from_party': 'PDK000592',
            'host': 'https://',
            'as4_use_discovery': True,
            'as4_sml_domain': 'acc.edelivery.tech.ec.europa.eu',
            'as4_signing_key': _Pem_Key,
            'as4_signing_cert_chain': _Pem_Certificate,
            'as4_decryption_key': _Pem_Key,
            'as4_trust_anchors': _Pem_Certificate,
        })

        _activate_create_tab(page, 'main')
        _screenshot(page, 'as4-outconn-main')

        _activate_create_tab(page, 'delivery')
        _screenshot(page, 'as4-outconn-delivery')

        _activate_create_tab(page, 'security')
        _screenshot(page, 'as4-outconn-security')
        _close_create_dialog(page)

        #
        # An outgoing ICS2 connection - push to customs with a static endpoint,
        # photographed on its Main tab
        #
        open_as4_outconn_page(page, base_url)
        open_create_dialog(page)

        fill_as4_outconn_form(page, {
            'name': 'ICS2 Conformance',
            'as4_profile': 'ics2',
            'as4_from_party': 'PL000000123456',
            'as4_to_party': 'sti-taxud',
            'host': 'https://conformance.customs.ec.europa.eu:443',
            'url_path': '/domibus/services/msh',
            'as4_signing_key': _Pem_Key,
            'as4_signing_cert_chain': _Pem_Certificate,
            'as4_decryption_key': _Pem_Key,
            'as4_trust_anchors': _Pem_Certificate,
        })

        _activate_create_tab(page, 'main')
        _screenshot(page, 'as4-outconn-ics2-main')
        _close_create_dialog(page)

        #
        # A Peppol channel - the access-point receiver - photographed on its Main tab,
        # its Participants tab with the serviced participants and its Routing tab
        #
        open_as4_channel_page(page, base_url)
        open_create_dialog(page)

        fill_as4_channel_form(page, {
            'name': 'Peppol Inbound',
            'url_path': '/peppol',
            'as4_profile': 'peppol',
            'as4_to_party': 'PDK000592',
            'as4_signing_key': _Pem_Key,
            'as4_signing_cert_chain': _Pem_Certificate,
            'as4_decryption_key': _Pem_Key,
            'as4_trust_anchors': _Pem_Certificate,
            'as4_serviced_participants': '0192:991825827\n0088:7315458756324',
            'service': 'invoicing.process-inbound',
        })

        _activate_create_tab(page, 'main')
        _screenshot(page, 'as4-channel-main')

        _activate_create_tab(page, 'security')
        _screenshot(page, 'as4-channel-security')

        _activate_create_tab(page, 'participants')
        _screenshot(page, 'as4-channel-participants')

        _activate_create_tab(page, 'routing')
        _screenshot(page, 'as4-channel-routing')
        _close_create_dialog(page)

# ################################################################################################################################
# ################################################################################################################################
