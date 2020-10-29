# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from operator import itemgetter

# Django
from django import forms

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.admin.web.forms import add_services, DataFormatForm
from zato.common.api import AMQP

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    def_id = forms.ChoiceField(widget=forms.Select())
    queue = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    consumer_tag_prefix = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    pool_size = forms.CharField(
        initial=AMQP.DEFAULT.POOL_SIZE, widget=forms.TextInput(attrs={'style':'width:10%', 'class':'required'}))
    ack_mode = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:20%'}))
    prefetch_count = forms.CharField(initial=AMQP.DEFAULT.PREFETCH_COUNT, widget=forms.TextInput(attrs={'style':'width:10%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        self.fields['def_id'].choices = []
        add_services(self, req)

        self.fields['ack_mode'].choices = []
        for item in AMQP.ACK_MODE():
            self.fields['ack_mode'].choices.append([item.id, item.name])

    def set_def_id(self, def_ids):
        # Sort AMQP definitions by their names.
        def_ids = sorted(iteritems(def_ids), key=itemgetter(1))

        for id, name in def_ids:
            self.fields['def_id'].choices.append([id, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
