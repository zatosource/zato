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
    parent_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, parent_id_list=None, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

        self.fields['parent_id'].choices = []
        for item in parent_id_list:
            self.fields['parent_id'].choices.append([item.id, item.name])

EditForm = CreateForm
