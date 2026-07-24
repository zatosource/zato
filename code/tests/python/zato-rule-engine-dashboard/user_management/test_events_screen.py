# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# Zato
from zato.rule_engine_dashboard.app.models import add_event, UserAction

# ################################################################################################################################

from user_test_helpers import new_account, signed_in_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The address the trail rows below are written with
_remote_addr = '198.51.100.7'

# How many events one page of the screen shows
_page_size = 50

# ################################################################################################################################
# ################################################################################################################################

def _add_trail(actor:'str', subject:'str', action:'str', count:'int'=1) -> 'None':
    """ Appends that many events to the trail.
    """
    for _ in range(count):
        _ = add_event(actor, action, subject, _remote_addr, 'is_active=False')

# ################################################################################################################################
# ################################################################################################################################

class TestEventsScreen:

    def test_newest_first(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        _add_trail('test.first.actor', 'test.first.subject', UserAction.Create)
        _add_trail('test.second.actor', 'test.second.subject', UserAction.Disable)

        response:'any_' = client.get('/events/')
        assert response.status_code == OK

        events = list(response.context['events'])

        assert events[0].subject == 'test.second.subject'
        assert events[1].subject == 'test.first.subject'

# ################################################################################################################################

    def test_filter_by_actor(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        _add_trail('test.wanted.actor', 'test.subject', UserAction.Create)
        _add_trail('test.other.actor', 'test.subject', UserAction.Create)

        response:'any_' = client.get('/events/', {'actor': 'wanted'})
        events = list(response.context['events'])

        assert len(events) == 1
        assert events[0].actor == 'test.wanted.actor'

# ################################################################################################################################

    def test_filter_by_subject(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        _add_trail('test.actor', 'test.wanted.subject', UserAction.Create)
        _add_trail('test.actor', 'test.other.subject', UserAction.Create)

        response:'any_' = client.get('/events/', {'subject': 'wanted'})
        events = list(response.context['events'])

        assert len(events) == 1
        assert events[0].subject == 'test.wanted.subject'

# ################################################################################################################################

    def test_filter_by_action(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        _add_trail('test.actor', 'test.subject', UserAction.Disable)
        _add_trail('test.actor', 'test.subject', UserAction.Enable)

        response:'any_' = client.get('/events/', {'action': UserAction.Disable})
        events = list(response.context['events'])

        assert len(events) == 1
        assert events[0].action == UserAction.Disable

# ################################################################################################################################

    def test_paging(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        beyond_one_page = _page_size + 5
        _add_trail('test.actor', 'test.subject', UserAction.Update, count=beyond_one_page)

        response:'any_' = client.get('/events/')
        first_page = response.context['events']

        assert len(first_page) == _page_size
        assert first_page.has_next()

        response = client.get('/events/', {'page': '2'})
        second_page = response.context['events']

        assert len(second_page) == 5
        assert not second_page.has_next()

# ################################################################################################################################

    def test_remote_address_is_shown(self:'any_') -> 'None':
        admin, _ = new_account(is_admin=True)
        client = signed_in_client(admin)

        _add_trail('test.actor', 'test.subject', UserAction.Create)

        response:'any_' = client.get('/events/')
        content = response.content.decode('utf8')

        assert _remote_addr in content

# ################################################################################################################################
# ################################################################################################################################
