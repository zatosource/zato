# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from operator import attrgetter

# Django
from django import forms

class CreateForm(forms.Form):
    cluster_id = forms.CharField(widget=forms.HiddenInput())
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    client_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        self.fields['client_id'].choices = []

    def set_client_id(self, client_ids):
        # Sort clients by their names.
        client_ids = sorted(client_ids, key=attrgetter('name'))

        for item in client_ids:
            self.fields['client_id'].choices.append([item.id, item.name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
