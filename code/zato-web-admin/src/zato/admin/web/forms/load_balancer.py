# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from operator import itemgetter

# Django
from django import forms

# Zato
from zato.common.haproxy import timeouts, http_log
from zato.common.util.api import make_repr

def populate_choices(form, fields_choices):
    """ A convenience function used in several places for populating a given
    form's SELECT choices.
    """
    for field_name, choices in fields_choices:
        form.fields[field_name].choices = []
        choices = sorted(choices.items(), key=itemgetter(0))
        for choice_id, choice_info in choices:
            choice_name = choice_info[1]
            form.fields[field_name].choices.append([choice_id, choice_name])

class ManageLoadBalancerForm(forms.Form):
    """ Form for the graphical management of HAProxy.
    """
    global_log_host = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:70%'}))
    global_log_port = forms.CharField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:70%'}))
    global_log_facility = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:70%'}))
    global_log_level = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:70%'}))

    timeout_connect = forms.CharField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:30%'}))
    timeout_client = forms.CharField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:30%'}))
    timeout_server = forms.CharField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:30%'}))

    http_plain_bind_address = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:70%'}))
    http_plain_bind_port = forms.CharField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:30%'}))
    http_plain_log_http_requests = forms.ChoiceField()
    http_plain_maxconn = forms.CharField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:30%'}))
    http_plain_monitor_uri = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:70%'}))

    def __init__(self, initial=None):
        initial = initial or {}
        super(ManageLoadBalancerForm, self).__init__(initial=initial)

        fields_choices = (
            ('http_plain_log_http_requests', http_log),
        )
        populate_choices(self, fields_choices)

    def __repr__(self):
        return make_repr(self)

class ManageLoadBalancerSourceCodeForm(forms.Form):
    """ Form for the source code-level management of HAProxy.
    """
    source_code = forms.CharField(widget=forms.Textarea(attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:400px'}))

class RemoteCommandForm(forms.Form):
    """ Form for the direct interface to HAProxy's commands.
    """
    command = forms.ChoiceField()
    timeout = forms.ChoiceField()
    extra = forms.CharField(widget=forms.TextInput(attrs={'style':'width:40%'}))
    result = forms.CharField(widget=forms.Textarea(attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:400px'}))

    def __init__(self, commands, initial=None):
        initial = initial or {}
        super(RemoteCommandForm, self).__init__(initial=initial)

        fields_choices = (
            ('command', commands),
            ('timeout', timeouts),
        )
        populate_choices(self, fields_choices)

    def __repr__(self):
        return make_repr(self)
