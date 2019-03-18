# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_services, DataFormatForm, INITIAL_CHOICES
from zato.common import SIMPLE_IO, WEB_SOCKET

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    service_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    security_id = forms.ChoiceField(widget=forms.Select())
    token_format = forms.ChoiceField(widget=forms.Select())
    new_token_wait_time = forms.CharField(initial=WEB_SOCKET.DEFAULT.NEW_TOKEN_TIMEOUT,
        widget=forms.TextInput(attrs={'style':'width:10%'}))
    token_ttl = forms.CharField(initial=WEB_SOCKET.DEFAULT.TOKEN_TTL,
        widget=forms.TextInput(attrs={'style':'width:20%'}))

    def __init__(self, security_list=[], prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['token_format'].choices = []
        self.fields['token_format'].choices.append(INITIAL_CHOICES)

        for name in sorted(dir(SIMPLE_IO.FORMAT)):
            if name.upper() == name:
                self.fields['token_format'].choices.append([name.lower(), name])

        add_security_select(self, security_list, field_name='security_id', needs_no_security=True, needs_rbac=False)
        add_services(self, req)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
