# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_services

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_zato = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    has_auto_reconnect = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    on_connect_service_name = forms.ChoiceField(widget=forms.Select())
    on_message_service_name = forms.ChoiceField(widget=forms.Select())
    on_close_service_name = forms.ChoiceField(widget=forms.Select())
    security_def = forms.ChoiceField(widget=forms.Select())
    subscription_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    def __init__(self, security_list=None, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_services(self, req, by_id=False)
        add_security_select(self, security_list, field_name='security_def', needs_rbac=False)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_zato = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    has_auto_reconnect = forms.BooleanField(required=False, widget=forms.CheckboxInput())
