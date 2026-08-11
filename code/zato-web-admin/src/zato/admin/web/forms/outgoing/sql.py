# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select_from_service
from zato.common.audit_log.sql import Level_Full, Level_Off, Level_Statement, Level_Statement_Params

# What each audit level means, in the order the dropdown shows them
audit_log_choices = (
    (Level_Off, 'Off'),
    (Level_Statement, 'Statements'),
    (Level_Statement_Params, 'Statements and parameters'),
    (Level_Full, 'Statements, parameters and rows'),
)

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    engine = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:50%'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:20%'}))
    db_name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:20%', 'autocomplete':'off'}))
    pool_size = forms.IntegerField(initial=10,
        widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:40px'}))
    audit_log = forms.ChoiceField(choices=audit_log_choices, widget=forms.Select(attrs={'style':'width:50%'}))
    extra = forms.CharField(widget=forms.Textarea(attrs={'style':'height:60px'}))

    def __init__(self, req, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_select_from_service(self, req, 'zato.outgoing.sql.get-engine-list', 'engine')

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
