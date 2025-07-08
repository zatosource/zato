# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select_from_service

class CreateForm(forms.Form):
    topic_id = forms.ChoiceField(widget=forms.Select())
    sec_base_id = forms.ChoiceField(widget=forms.Select())
    pattern_matched = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        if req:
            add_select_from_service(self, req, 'zato.pubsub.topic.get-list', 'topic_id', True)
            add_select_from_service(self, req, 'zato.security.get-list', 'sec_base_id', True)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
