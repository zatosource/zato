# -*- coding: utf-8 -*-
"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io
Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The wizard's edit page, opened on a channel that has no value stored under one of its switches - the switch has to
# open the way the server runs it, which is as its default, and a switch stored off has to open off.

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.hl7.mllp.fields import Channel_Fields

# Zato - Dashboard
from zato.admin.web.forms import populate_form_initial
from zato.admin.web.forms.channel.hl7.mllp import EditForm

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist
    any_ = any_
    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class _FakeClient:
    """ Answers the listings the form's selects ask for with nothing.
    """
    def invoke(self, service:'str', request:'anydict') -> 'any_':
        if service == 'zato.service.get-list':
            out = Bunch(data=[])
        else:
            out = []
        return out

# ################################################################################################################################

@pytest.fixture
def req() -> 'any_':
    out = Bunch()
    out.zato = Bunch()
    out.zato.client = _FakeClient()
    out.zato.cluster_id = 1
    return out

# ################################################################################################################################

def _get_switches_on_by_default() -> 'strlist':
    """ Every switch of a channel whose default is on, except is_active, which is a column a stored channel always has.
    """
    out:'strlist' = []
    for field in Channel_Fields:
        if field.default is True and not field.is_column:
            out.append(field.name)
    return out

# ################################################################################################################################

def _is_checked(form:'any_', name:'str') -> 'bool':
    html = str(form[name])
    return 'checked' in html

# ################################################################################################################################
# ################################################################################################################################

class TestEditFormSwitches:

# ################################################################################################################################

    def test_a_switch_the_channel_has_no_value_under_opens_as_its_default(self, req:'any_') -> 'None':
        """ The server runs a channel with a missing switch as the switch's default, so the edit page opens it
        the same way - saving the page unchanged then stores what the server was running.
        """
        switches = _get_switches_on_by_default()
        assert switches

        form = EditForm(prefix='edit', req=req)
        populate_form_initial(form, {})

        for name in switches:
            assert _is_checked(form, name), name

        assert not _is_checked(form, 'fix_off_by_one_field_index')

# ################################################################################################################################

    def test_a_switch_stored_off_opens_off(self, req:'any_') -> 'None':

        item = {}
        for name in _get_switches_on_by_default():
            item[name] = False

        form = EditForm(prefix='edit', req=req)
        populate_form_initial(form, item)

        for name in _get_switches_on_by_default():
            assert not _is_checked(form, name), name

# ################################################################################################################################

    def test_a_switch_stored_on_opens_on(self, req:'any_') -> 'None':

        form = EditForm(prefix='edit', req=req)
        populate_form_initial(form, {'fix_off_by_one_field_index': True, 'is_active': True})

        assert _is_checked(form, 'fix_off_by_one_field_index')
        assert _is_checked(form, 'is_active')

# ################################################################################################################################
# ################################################################################################################################
