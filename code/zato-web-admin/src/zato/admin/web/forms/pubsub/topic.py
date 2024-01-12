# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import PUBSUB
from zato.admin.web.forms import add_select, add_pubsub_services

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    has_gd = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_api_sub_allowed = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    hook_service_id = forms.ChoiceField(widget=forms.Select())
    on_no_subs_pub = forms.ChoiceField(widget=forms.Select())

    max_depth_gd = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:20%'}), initial=PUBSUB.DEFAULT.TOPIC_MAX_DEPTH_GD)
    max_depth_non_gd = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:20%'}), initial=PUBSUB.DEFAULT.TOPIC_MAX_DEPTH_NON_GD)

    depth_check_freq = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:15%'}), initial=PUBSUB.DEFAULT.DEPTH_CHECK_FREQ)

    pub_buffer_size_gd = forms.CharField(widget=forms.HiddenInput(), initial=PUBSUB.DEFAULT.PUB_BUFFER_SIZE_GD)

    task_sync_interval = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:20%'}), initial=PUBSUB.DEFAULT.TASK_SYNC_INTERVAL)

    task_delivery_interval = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:15%'}), initial=PUBSUB.DEFAULT.TASK_DELIVERY_INTERVAL)

    limit_retention = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:15%'}), initial=PUBSUB.DEFAULT.LimitTopicRetention)

    limit_message_expiry = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:15%'}), initial=PUBSUB.DEFAULT.LimitMessageExpiry)

    limit_sub_inactivity = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:15%'}), initial=PUBSUB.DEFAULT.LimitSubInactivity)

    def __init__(self, req, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        add_select(self, 'on_no_subs_pub', [
            PUBSUB.ON_NO_SUBS_PUB.ACCEPT, PUBSUB.ON_NO_SUBS_PUB.DROP,
        ], False)
        add_pubsub_services(self, req, by_id=True)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
