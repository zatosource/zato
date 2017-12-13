# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import PUBSUB
from zato.admin.web.forms import add_pubsub_services

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    has_gd = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_api_sub_allowed = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    max_depth_gd = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:20%'}), initial=PUBSUB.DEFAULT.TOPIC_MAX_DEPTH_GD)
    max_depth_non_gd = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:20%'}), initial=PUBSUB.DEFAULT.TOPIC_MAX_DEPTH_NON_GD)
    gd_depth_check_freq = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:20%'}), initial=PUBSUB.DEFAULT.GD_DEPTH_CHECK_FREQ)
    hook_service_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, req, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        add_pubsub_services(self, req, by_id=True)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
