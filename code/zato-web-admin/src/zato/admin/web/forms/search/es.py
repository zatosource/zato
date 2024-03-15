# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import SEARCH

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    hosts = forms.CharField(
        initial=SEARCH.ES.DEFAULTS.HOSTS, widget=forms.Textarea(attrs={'style':'width:100%', 'class':'required'}))
    timeout = forms.CharField(initial=90, widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))
    body_as = forms.CharField(initial=SEARCH.ES.DEFAULTS.BODY_AS,
        widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
