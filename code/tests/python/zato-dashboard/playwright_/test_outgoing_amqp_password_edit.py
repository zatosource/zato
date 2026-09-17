# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.cli.enmasse.client import get_session_from_server_dir
from zato.cli.enmasse.util.secrets import decrypt_secret
from zato.common.const import SECRETS
from zato.common.crypto.api import CryptoManager
from zato.common.odb.model import ChannelAMQP, OutgoingAMQP
from zato.common.test.playwright_pubsub import create_amqp_channel, create_outgoing_amqp, navigate_to_page, submit_edit_form
from zato.common.typing_ import cast_
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, strtuple

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.amqp.password.' + CryptoManager.generate_hex_string(32) + '.'

_Outgoing_AMQP_Page_Url = '/zato/outgoing/amqp/?cluster=1'
_Channel_AMQP_Page_Url = '/zato/channel/amqp/?cluster=1'

# The JS namespaces the edit dialogs of both pages are opened through
_Outgoing_AMQP_Namespace = 'outgoing.amqp'
_Channel_AMQP_Namespace = 'channel.amqp'

# The service every test channel invokes
_Channel_Service = 'demo.ping'

_Username = 'amqp.user'
_Queue = 'amqp.queue'

# An edit stops the consumers of a channel first and each of them is in the middle of a reconnect attempt
# to a broker that does not exist, so a single edit may take well over ten seconds to complete.
_Edit_Timeout = 90000

# ################################################################################################################################
# ################################################################################################################################

def _new_password() -> 'str':
    """ Returns a password no other object could have.
    """
    out = 'amqp-password-' + CryptoManager.generate_hex_string()
    return out

# ################################################################################################################################

def _new_address() -> 'str':
    """ Returns an address of a broker that does not exist - a free local port nothing listens on.
    """
    port = get_free_port()
    out = f'amqp://127.0.0.1:{port}//'
    return out

# ################################################################################################################################

def _open_edit_dialog(page:'Page', namespace:'str', item_id:'str') -> 'None':
    """ Opens the edit dialog of an item on either of the AMQP pages.
    """
    page.evaluate(f'$.fn.zato.{namespace}.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def _get_stored_password(server_dir:'str', model:'any_', name:'str') -> 'strtuple':
    """ Returns the password of the row of the given name as it is stored, along with its clear-text form.
    """
    session = get_session_from_server_dir(server_dir)
    try:
        row = session.query(model).filter_by(name=name).one()
        stored = row.password

        # The column is not nullable, so a row always has a string here
        decrypted = decrypt_secret(session, stored)
        clear = cast_('str', decrypted)
    finally:
        session.close()

    out = stored, clear
    return out

# ################################################################################################################################

def _assert_stored_password(server_dir:'str', model:'any_', name:'str', expected:'str') -> 'None':
    """ Asserts that the row keeps its password encrypted and that it decrypts to what is expected.
    """
    stored, clear = _get_stored_password(server_dir, model, name)

    assert stored.startswith(SECRETS.PREFIX), f'Password of `{name}` is not encrypted -> `{stored}`'
    assert clear == expected, f'Password of `{name}` is `{clear}`, expected `{expected}`'

# ################################################################################################################################

def _assert_page_hides(page:'Page', base_url:'str', page_url:'str', *passwords:'str') -> 'None':
    """ Reloads a page and asserts that its HTML carries no password in any form.
    """
    navigate_to_page(page, base_url, page_url)
    html = page.content()

    for password in passwords:
        assert password not in html, f'Page `{page_url}` shows a password in clear text'

    assert SECRETS.PREFIX not in html, f'Page `{page_url}` shows an encrypted password'

# ################################################################################################################################

def _edit(
    page:'Page',
    base_url:'str',
    page_url:'str',
    namespace:'str',
    item_id:'str',
    username:'str',
    password:'str',
    ) -> 'None':
    """ Reloads the page, opens the edit dialog, asserts its password field is blank, sets the username
    and the password as given - a blank password is left blank - and saves the form.
    """

    # The page is loaded afresh so the form is filled from the listing alone, not from what the browser
    # still remembers of the create form it submitted a moment ago
    navigate_to_page(page, base_url, page_url)
    _open_edit_dialog(page, namespace, item_id)

    field_password = page.input_value('#id_edit-password')
    assert field_password == '', f'Edit form carries a password -> `{field_password}`'

    page.fill('#id_edit-username', username)

    if password:
        page.fill('#id_edit-password', password)

    submit_edit_form(page, _Edit_Timeout)

# ################################################################################################################################
# ################################################################################################################################

class TestAMQPPasswordEdit:
    """ The AMQP forms never receive the stored password and a blank password on edit keeps the stored one.
    """

# ################################################################################################################################

    def test_outgoing_amqp_password_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ An outgoing AMQP connection keeps its encrypted password across an edit with a blank password field
        and changes it on an edit that gives a new one.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_dir = zato_dashboard['server_dir']

        name = _Test_Name_Prefix + 'outconn'
        password_first = _new_password()
        password_second = _new_password()

        # Create the connection with the first password ..
        item_id = create_outgoing_amqp(page, base_url, name, _new_address(), _Username, password_first)
        _assert_stored_password(server_dir, OutgoingAMQP, name, password_first)

        # .. an edit that leaves the password blank keeps the stored one ..
        _edit(page, base_url, _Outgoing_AMQP_Page_Url, _Outgoing_AMQP_Namespace, item_id, _Username + '.edited', '')
        _assert_stored_password(server_dir, OutgoingAMQP, name, password_first)

        # .. an edit that gives a new password replaces the stored one ..
        _edit(page, base_url, _Outgoing_AMQP_Page_Url, _Outgoing_AMQP_Namespace, item_id, _Username, password_second)
        _assert_stored_password(server_dir, OutgoingAMQP, name, password_second)

        # .. and the page shows neither of them in any form.
        _assert_page_hides(page, base_url, _Outgoing_AMQP_Page_Url, password_first, password_second)

# ################################################################################################################################

    def test_channel_amqp_password_edit(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ An AMQP channel keeps its encrypted password across an edit with a blank password field
        and changes it on an edit that gives a new one.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_dir = zato_dashboard['server_dir']

        name = _Test_Name_Prefix + 'channel'
        password_first = _new_password()
        password_second = _new_password()

        # Create the channel with the first password ..
        item_id = create_amqp_channel(
            page, base_url, name, _new_address(), _Username, password_first, _Queue, _Channel_Service)
        _assert_stored_password(server_dir, ChannelAMQP, name, password_first)

        # .. an edit that leaves the password blank keeps the stored one ..
        _edit(page, base_url, _Channel_AMQP_Page_Url, _Channel_AMQP_Namespace, item_id, _Username + '.edited', '')
        _assert_stored_password(server_dir, ChannelAMQP, name, password_first)

        # .. an edit that gives a new password replaces the stored one ..
        _edit(page, base_url, _Channel_AMQP_Page_Url, _Channel_AMQP_Namespace, item_id, _Username, password_second)
        _assert_stored_password(server_dir, ChannelAMQP, name, password_second)

        # .. and the page shows neither of them in any form.
        _assert_page_hides(page, base_url, _Channel_AMQP_Page_Url, password_first, password_second)

# ################################################################################################################################
# ################################################################################################################################
