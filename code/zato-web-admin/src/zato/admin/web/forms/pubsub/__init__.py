# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select
from zato.common.api import PUBSUB

# ################################################################################################################################

class MsgForm(forms.Form):
    correl_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    in_reply_to = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    expiration = forms.CharField(
        widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}),
        initial=PUBSUB.DEFAULT.EXPIRATION)
    exp_from_now = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    priority = forms.CharField(required=True,
        widget=forms.TextInput(attrs={'class':'required', 'style':'width:60%'}), initial=5)
    mime_type = forms.CharField(widget=forms.HiddenInput())

# ################################################################################################################################

class MsgPublishForm(MsgForm):
    topic_name = forms.ChoiceField(widget=forms.Select())
    publisher_id = forms.ChoiceField(widget=forms.Select())
    gd = forms.ChoiceField(widget=forms.Select())
    ext_client_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    group_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    msg_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    position_in_group = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:30%'}))
    select_changer_source = forms.CharField(widget=forms.Textarea(attrs={'style':'display:none'}))
    reply_to_sk = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%;margin-bottom:4px'}))
    deliver_to_sk = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    def __init__(self, req, select_changer_data, initial_topic_name, topic_list, initial_hook_service_name, publisher_list,
            *args, **kwargs):
        super(MsgPublishForm, self).__init__(*args, **kwargs)
        add_select(self, 'topic_name', topic_list)
        add_select(self, 'publisher_id', publisher_list)
        add_select(self, 'gd', PUBSUB.GD_CHOICE(), False)

        self.initial['topic_name'] = initial_topic_name
        self.initial['select_changer_source'] = select_changer_data

# ################################################################################################################################
