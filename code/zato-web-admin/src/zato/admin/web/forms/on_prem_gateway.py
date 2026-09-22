# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone

    # Dummy assignments to satisfy type checkers
    any_ = any_
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

_hosts_placeholder = 'erp-db.corp.local:5432\ncrm.corp.local:443'

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_key_reset_required = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    hosts = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'style':'width:100%; height:120px', 'placeholder':_hosts_placeholder}))

    def __init__(self, prefix:'strnone'=None, req:'any_'=None) -> 'None':
        super(CreateForm, self).__init__(prefix=prefix)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_key_reset_required = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
