# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, WithRateLimiting

class CreateForm(WithRateLimiting):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_path = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    security_id = forms.ChoiceField(widget=forms.Select())
    service_whitelist = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:100px'}))
    is_rate_limit_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    rate_limit_check_parent_def = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    def __init__(self, security_list=None, prefix=None, post_data=None, req=None):
        security_list = security_list or []
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_security_select(self, security_list, field_name='security_id')

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    rate_limit_check_parent_def = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
