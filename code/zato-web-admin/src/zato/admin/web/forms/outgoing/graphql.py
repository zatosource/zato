# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    default_query_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial='60', required=False)
    security_id = forms.ChoiceField(widget=forms.Select())
    extra = forms.CharField(widget=forms.Textarea(attrs={'style':'height:60px'}), required=False)

    def __init__(self, req, security_list, prefix=None):
        super(CreateForm, self).__init__(prefix=prefix)
        add_security_select(self, security_list, field_name='security_id')

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
