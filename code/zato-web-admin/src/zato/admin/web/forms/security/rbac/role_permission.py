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
    role_id = forms.ChoiceField(widget=forms.Select())
    service_id = forms.ChoiceField(widget=forms.Select())
    perm_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, role_id_list, service_id_list, perm_id_list, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

        self.fields['role_id'].choices = []
        for item in role_id_list:
            self.fields['role_id'].choices.append([item.id, item.name])

        self.fields['service_id'].choices = []
        for item in service_id_list:
            self.fields['service_id'].choices.append([item.id, item.name])

        self.fields['perm_id'].choices = []
        for item in perm_id_list:
            self.fields['perm_id'].choices.append([item.id, item.name])
