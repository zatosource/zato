# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from operator import itemgetter

# Django
from django import forms

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.common.api import AMQP

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    delivery_mode = forms.ChoiceField(widget=forms.Select())
    priority = forms.CharField(initial=AMQP.DEFAULT.PRIORITY, widget=forms.TextInput(attrs={'style':'width:5%'}))
    content_type = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    content_encoding = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    expiration = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    pool_size = forms.CharField(
        initial=AMQP.DEFAULT.POOL_SIZE, widget=forms.TextInput(attrs={'style':'width:10%', 'class':'required'}))
    user_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    app_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    def_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['delivery_mode'].choices = []
        self.fields['def_id'].choices = []

        # Sort modes by their friendly name.
        modes = sorted(iteritems(delivery_friendly_name), key=itemgetter(1))

        for mode, friendly_name in modes:
            self.fields['delivery_mode'].choices.append([mode, friendly_name])

    def set_def_id(self, def_ids):
        # Sort AMQP definitions by their names.
        def_ids = sorted(iteritems(def_ids), key=itemgetter(1))

        for id, name in def_ids:
            self.fields['def_id'].choices.append([id, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
