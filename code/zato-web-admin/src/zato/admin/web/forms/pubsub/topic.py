# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    """ Form for creating a pub/sub topic.
    """
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'style':'width:90%; height:80px'}), required=False)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    """ Form for editing a pub/sub topic.
    """
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
