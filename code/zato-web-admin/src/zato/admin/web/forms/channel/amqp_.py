# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services, DataFormatForm
from zato.common.api import AMQP

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    queue = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    consumer_tag_prefix = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    pool_size = forms.CharField(
        initial=AMQP.DEFAULT.POOL_SIZE, widget=forms.TextInput(attrs={'style':'width:10%', 'class':'required'}))
    ack_mode = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:20%'}))
    prefetch_count = forms.CharField(initial=AMQP.DEFAULT.PREFETCH_COUNT, widget=forms.TextInput(attrs={'style':'width:10%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_services(self, req)

        self.fields['ack_mode'].choices = []
        for item in AMQP.ACK_MODE():
            self.fields['ack_mode'].choices.append([item.id, item.name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
