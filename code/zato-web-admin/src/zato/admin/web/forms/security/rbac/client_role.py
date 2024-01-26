# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class CreateForm(forms.Form):

    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    client_def = forms.ChoiceField(widget=forms.Select())
    role_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, client_def_list, role_id_list, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

        self.fields['client_def'].choices = []
        for item in client_def_list:
            self.fields['client_def'].choices.append([item.client_def, item.client_name])

        self.fields['role_id'].choices = []
        for item in role_id_list:
            self.fields['role_id'].choices.append([item.id, item.name])
