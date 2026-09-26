# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_select, add_services
from zato.common.api import KAFKA

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.admin.web.views import SecurityList
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial='localhost:9092')
    topic = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    group_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    security_id = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    sasl_mechanism = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    ssl = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    ssl_ca_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_cert_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_key_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    def __init__(
        self,
        req:'any_',
        security_list:'SecurityList',
        prefix:'strnone' = None,
        post_data:'any_' = None,
    ) -> 'None':
        super().__init__(post_data, prefix=prefix)
        sasl_mechanisms = KAFKA.SASL_MECHANISM()
        add_services(self, req)
        add_security_select(self, security_list, field_name='security_id')
        add_select(self, 'sasl_mechanism', sasl_mechanisms, needs_initial_select=True)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
