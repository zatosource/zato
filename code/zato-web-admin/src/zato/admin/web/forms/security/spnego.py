# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    principal = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    keytab_path = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    target_spn = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    needs_delegation = forms.BooleanField(required=False, widget=forms.CheckboxInput())

class EditForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    principal = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    keytab_path = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    target_spn = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    needs_delegation = forms.BooleanField(required=False, widget=forms.CheckboxInput())
