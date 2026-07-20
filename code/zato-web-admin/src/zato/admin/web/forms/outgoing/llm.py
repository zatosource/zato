# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import LLM
from zato.common.llm_models import model_list

# ################################################################################################################################
# ################################################################################################################################

# The form initially suggests the first catalog model's wire id and its provider's address
_default_model = model_list[0]['id']

_provider_address = {
    LLM.PROVIDER.CLAUDE.id: LLM.ADDRESS.CLAUDE,
    LLM.PROVIDER.OPENAI.id: LLM.ADDRESS.OPENAI,
    LLM.PROVIDER.GEMINI.id: LLM.ADDRESS.GEMINI,
}

_default_address = _provider_address[model_list[0]['provider']]

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    model = forms.CharField(initial=_default_model, widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))
    address = forms.CharField(
        initial=_default_address, widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))

    # The initial address is a hosted provider's, so the key starts out required -
    # the JS drops the requirement when the address points at a self-hosted endpoint.
    secret = forms.CharField(
        required=False, strip=False, widget=forms.PasswordInput(attrs={'class':'required', 'style':'width:100%'}))

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

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # The edit dialog has no API key field - the key is changed through the Change API key link
    secret = None

# ################################################################################################################################
# ################################################################################################################################
