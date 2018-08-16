# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from operator import itemgetter

# Django
from django import forms

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.common.odb import WMQ_DEFAULT_PRIORITY

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    delivery_mode = forms.ChoiceField(widget=forms.Select())
    priority = forms.CharField(initial=WMQ_DEFAULT_PRIORITY, widget=forms.TextInput(attrs={'style':'width:5%'}))
    expiration = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    def_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['delivery_mode'].choices = []
        self.fields['def_id'].choices = []

        # Sort modes by their friendly name.
        modes = sorted(delivery_friendly_name.iteritems(), key=itemgetter(1))

        for mode, friendly_name in modes:
            self.fields['delivery_mode'].choices.append([mode, friendly_name])

    def set_def_id(self, def_ids):
        # Sort definitions by their names.
        def_ids = sorted(def_ids.iteritems(), key=itemgetter(1))

        for id, name in def_ids:
            self.fields['def_id'].choices.append([id, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
