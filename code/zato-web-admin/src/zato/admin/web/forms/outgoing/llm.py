# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select
from zato.common.api import LLM

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    provider = forms.ChoiceField(widget=forms.Select())
    address = forms.CharField(
        initial=LLM.DEFAULT.Address, widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    model = forms.CharField(initial=LLM.DEFAULT.Model, widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))

    pool_size = forms.CharField(
        initial=LLM.DEFAULT.POOL_SIZE, widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:9%'}))
    timeout = forms.CharField(
        initial=LLM.DEFAULT.TIMEOUT, widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:9%'}))
    max_tokens = forms.CharField(
        initial=LLM.DEFAULT.MAX_TOKENS, widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:9%'}))

    max_history_turns = forms.CharField(
        initial=LLM.DEFAULT.MAX_HISTORY_TURNS,
        widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:9%'}))
    chat_expiry = forms.CharField(
        initial=LLM.DEFAULT.CHAT_EXPIRY, widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:9%'}))

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        add_select(self, 'provider', LLM.PROVIDER(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
