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
    http_soap_id = forms.ChoiceField(widget=forms.Select())
    max_backlog = forms.CharField(
        initial=PUB_SUB.DEFAULT_MAX_BACKLOG, widget=forms.TextInput(attrs={'class':'required', 'style':'width:20%'}))

    def __init__(self, prefix=None, post_data=None, client_ids=None, http_soap_ids=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        for name in('client_id', 'delivery_mode', 'client_id', 'http_soap_id'):
            self.fields[name].choices = []

        self.set_items(PUB_SUB.DELIVERY_MODE, 'delivery_mode')
        self.set_items(client_ids or [], 'client_id')
        self.set_items(http_soap_ids or [], 'http_soap_id')

    def set_items(self, ids, field_name):
        ids = sorted(ids, key=attrgetter('name'))

        for item in ids:
            self.fields[field_name].choices.append([item.id, item.name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
