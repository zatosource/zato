# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services, INITIAL_CHOICES
from zato.common import NOTIF

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    def_id = forms.ChoiceField(widget=forms.Select())
    interval = forms.CharField(initial=NOTIF.DEFAULT.CHECK_INTERVAL_SQL, widget=forms.TextInput(attrs={'style':'width:15%'}))
    service_name = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    query = forms.CharField(widget=forms.Textarea(attrs={'class':'required', 'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None, sql_defs=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['def_id'].choices[:] = []
        self.fields['def_id'].choices.append(INITIAL_CHOICES)

        for item in sql_defs:
            self.fields['def_id'].choices.append([item.id, item.name])

        add_services(self, req)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
