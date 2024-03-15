# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import WithRateLimiting

class CreateForm(WithRateLimiting):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    realm = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    is_rate_limit_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    rate_limit_check_parent_def = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
