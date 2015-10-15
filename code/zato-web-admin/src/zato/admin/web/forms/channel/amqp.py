# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from operator import itemgetter

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services, DataFormatForm

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    def_id = forms.ChoiceField(widget=forms.Select())
    queue = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    consumer_tag_prefix = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    is_sync = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    nack_timeout = forms.IntegerField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:30px'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        self.fields['def_id'].choices = []
        add_services(self, req)

    def set_def_id(self, def_ids):
        # Sort AMQP definitions by their names.
        def_ids = sorted(def_ids.iteritems(), key=itemgetter(1))

        for id, name in def_ids:
            self.fields['def_id'].choices.append([id, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
