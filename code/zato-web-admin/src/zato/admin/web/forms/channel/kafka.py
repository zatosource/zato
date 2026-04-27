# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial='localhost:9092')
    topic = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    group_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    service = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    ssl_ca_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_cert_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_key_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
