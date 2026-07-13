# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_health_check_fields, add_security_select, add_services
from zato.admin.web.forms.http_soap import callback_type_choices, response_map_mode_choices, scheduler_run_unit_choices
from zato.common.api import DEFAULT_HTTP_PING_METHOD, MISC, SOAP_VERSIONS

# ################################################################################################################################
# ################################################################################################################################

_validate_tls_choices = [
    (True, 'Yes'),
    (False, 'No'),
]

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    # Main
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(initial='https://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(required=False, initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_action = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    timeout = forms.CharField(initial=MISC.DEFAULT_HTTP_TIMEOUT, widget=forms.TextInput(attrs={'style':'width:10%'}))

    # SOAP
    soap_version = forms.ChoiceField(widget=forms.Select())
    use_ws_addressing = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_mtom = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # Security
    security_id = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    validate_tls = forms.ChoiceField(widget=forms.Select())
    tls_client_cert = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_client_key = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Body credentials - a JSON list of mapping rows managed in JavaScript
    body_credentials = forms.CharField(required=False, widget=forms.HiddenInput())

    # More
    ping_method = forms.CharField(initial=DEFAULT_HTTP_PING_METHOD, widget=forms.TextInput(attrs={'style':'width:20%'}))
    content_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    serialization_type = forms.CharField(initial='string', widget=forms.HiddenInput())

    # Request - what request each invocation builds. The message and SOAP header rows are edited
    # as rows of widgets and serialized by JS to the hidden JSON fields below before the form is submitted.
    request_operation = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    request_message = forms.CharField(required=False, widget=forms.HiddenInput())
    request_message_map = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%; height:4rem'}))
    request_soap_headers = forms.CharField(required=False, widget=forms.HiddenInput())

    # Request - the WS-Addressing values injected into every envelope
    wsa_action = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    wsa_to = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    wsa_reply_to = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Response - how to transform the response before the callback receives it
    response_map = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%; height:4rem'}))
    response_map_mode = forms.ChoiceField(required=False, widget=forms.Select())

    # Callback - where to deliver the response
    callback_type = forms.ChoiceField(required=False, widget=forms.Select())
    callback_service = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    callback_topic = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    callback_rest = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))

    # Scheduler - when to invoke the connection
    scheduler_run_every = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:12%'}))
    scheduler_run_unit = forms.ChoiceField(required=False, widget=forms.Select())
    scheduler_start_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%; height:19px'}))
    scheduler_job_id = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, security_list=None, prefix=None, post_data=None, req=None):
        security_list = security_list or []
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['soap_version'].choices = []
        for name in sorted(SOAP_VERSIONS):
            self.fields['soap_version'].choices.append([name, name])

        self.fields['validate_tls'].choices = []
        for value, label in _validate_tls_choices:
            self.fields['validate_tls'].choices.append([value, label])

        self.fields['scheduler_run_unit'].choices = []
        for value, label in scheduler_run_unit_choices:
            self.fields['scheduler_run_unit'].choices.append([value, label])

        self.fields['callback_type'].choices = []
        for value, label in callback_type_choices:
            self.fields['callback_type'].choices.append([value, label])

        self.fields['response_map_mode'].choices = []
        for value, label in response_map_mode_choices:
            self.fields['response_map_mode'].choices.append([value, label])

        # The generic health check tab shares its fields across connection types
        add_health_check_fields(self)

        add_security_select(self, security_list, field_name='security_id')

        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
