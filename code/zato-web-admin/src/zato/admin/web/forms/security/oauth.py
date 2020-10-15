# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import MISC, NONCE_STORE

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    sig_method = forms.ChoiceField(widget=forms.Select())
    max_nonce_log = forms.IntegerField(initial=NONCE_STORE.DEFAULT_MAX_LOG,
        widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:20%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        self.fields['sig_method'].choices = []

        for sig_method in MISC.OAUTH_SIG_METHODS:
            self.fields['sig_method'].choices.append([sig_method, sig_method])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
