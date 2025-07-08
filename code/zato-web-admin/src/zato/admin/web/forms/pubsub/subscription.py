# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select_from_service
from zato.admin.web.util import get_pubsub_security_choices

class CreateForm(forms.Form):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    topic_id = forms.ChoiceField(widget=forms.Select())
    sec_base_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        if req:
            add_select_from_service(self, req, 'zato.pubsub.topic.get-list', 'topic_id', True)
            # Use filtered security definitions for PubSub clients
            self.fields['sec_base_id'].choices = get_pubsub_security_choices(req, 'create')

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def __init__(self, prefix=None, post_data=None, req=None):
        super(EditForm, self).__init__(prefix, post_data, req)
        if req:
            # Use filtered security definitions for edit (allows all available ones)
            self.fields['sec_base_id'].choices = get_pubsub_security_choices(req, 'edit')
