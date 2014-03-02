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

# Zato
from zato.common import PUB_SUB

class CreateForm(forms.Form):
    cluster_id = forms.CharField(widget=forms.HiddenInput())
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    client_id = forms.ChoiceField(widget=forms.Select())
    delivery_mode = forms.ChoiceField(widget=forms.Select())
    callback = forms.CharField(initial='', widget=forms.TextInput(attrs={'style':'width:90%'}))
    max_backlog = forms.CharField(
        initial=PUB_SUB.DEFAULT_MAX_BACKLOG, widget=forms.TextInput(attrs={'class':'required', 'style':'width:20%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        self.fields['client_id'].choices = []
        self.fields['delivery_mode'].choices = []

        for item in PUB_SUB.DELIVERY_MODE:
            self.fields['delivery_mode'].choices.append([item.id, item.name])

    def set_client_id(self, client_ids):
        # Sort clients by their names.
        client_ids = sorted(client_ids, key=attrgetter('name'))

        for item in client_ids:
            self.fields['client_id'].choices.append([item.id, item.name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
