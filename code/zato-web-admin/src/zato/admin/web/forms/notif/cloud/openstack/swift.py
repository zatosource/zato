# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services
from zato.common import NOTIF

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    interval = forms.CharField(initial=NOTIF.DEFAULT.CHECK_INTERVAL, widget=forms.TextInput(attrs={'style':'width:10%'}))
    name_pattern = forms.CharField(initial=NOTIF.DEFAULT.NAME_PATTERN, widget=forms.TextInput(attrs={'style':'width:100%'}))

    containers = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))
    service_name = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))

    name_pattern_neg = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    get_data = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    get_data_patt = forms.CharField(initial=NOTIF.DEFAULT.GET_DATA_PATTERN, widget=forms.TextInput(attrs={'style':'width:70%'}))
    get_data_patt_neg = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, def_list=None, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['def_id'].choices = []
        for item in def_list:
            self.fields['def_id'].choices.append([item.id, item.name])

        add_services(self, req)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    get_data = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    get_data_patt_neg = forms.BooleanField(required=False, widget=forms.CheckboxInput())
