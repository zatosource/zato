# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.util import get_server_user_conf_directory
from zato.common.api import LLM
from zato.common.llm_models import get_model_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_provider_address = {
    LLM.PROVIDER.CLAUDE.id: LLM.ADDRESS.CLAUDE,
    LLM.PROVIDER.OPENAI.id: LLM.ADDRESS.OPENAI,
    LLM.PROVIDER.GEMINI.id: LLM.ADDRESS.GEMINI,
}

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    model = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))

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

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        # The form initially suggests the first catalog model's wire id and its provider's address,
        # with the catalog read afresh so edits to default-models.yaml show up without a restart.
        user_conf_directory = get_server_user_conf_directory()
        model_list = get_model_list(user_conf_directory)
        first_model = model_list[0]

        self.fields['model'].initial = first_model['id']
        self.fields['address'].initial = _provider_address[first_model['provider']]

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # The edit dialog has no API key field - the key is changed through the Change API key link
    secret = None

# ################################################################################################################################
# ################################################################################################################################
