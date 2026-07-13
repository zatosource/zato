# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_health_check_fields, add_security_select, add_services, \
    SearchForm as _ChooseClusterForm, DataFormatForm
from zato.common.api import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, HTTP_SOAP, MISC, PARAMS_PRIORITY, IO, SOAP_VERSIONS, URL_PARAMS_PRIORITY

# ################################################################################################################################

params_priority = (
    (PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG, 'URL over message'),
    (PARAMS_PRIORITY.MSG_OVER_CHANNEL_PARAMS, 'Message over URL'),
)

# ################################################################################################################################

url_params_priority = (
    (URL_PARAMS_PRIORITY.QS_OVER_PATH, 'QS over path'),
    (URL_PARAMS_PRIORITY.PATH_OVER_QS, 'Path over QS'),
)

validate_tls_choices = (
    (True, 'Yes'),
    (False, 'No'),
)

# ################################################################################################################################

scheduler_run_unit_choices = (
    ('seconds', 'seconds'),
    ('minutes', 'minutes'),
    ('hours', 'hours'),
    ('days', 'days'),
)

# ################################################################################################################################

# The empty first choice means no callback is configured at all
callback_type_choices = (
    ('', '----------'),
    ('service', 'Service'),
    ('topic', 'Pub/sub topic'),
    ('rest', 'REST connection'),
)

# ################################################################################################################################

request_value_mode_choices = (
    ('text', 'Send as typed'),
    ('jsonata', 'Evaluate as JSONata'),
)

# ################################################################################################################################

response_map_mode_choices = (
    ('jsonata', 'JSONata'),
    ('xpath', 'XPath'),
)

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(initial='http://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    match_slash = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_params_pri = forms.ChoiceField(widget=forms.Select())
    params_pri = forms.ChoiceField(widget=forms.Select())
    serialization_type = forms.CharField(widget=forms.HiddenInput(), initial='string')
    method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    soap_action = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_version = forms.ChoiceField(widget=forms.Select())
    use_mtom = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    ping_method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}))
    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=MISC.DEFAULT_HTTP_TIMEOUT)
    security = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    content_type = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())
    data_formats_allowed = IO.HTTP_SOAP_FORMAT
    http_accept = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=HTTP_SOAP.ACCEPT.ANY)
    validate_tls = forms.ChoiceField(widget=forms.Select())

    data_encoding = forms.CharField(widget=forms.HiddenInput())

    # Scheduler - when to invoke the connection
    scheduler_run_every = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:12%'}))
    scheduler_run_unit = forms.ChoiceField(required=False, widget=forms.Select())
    scheduler_start_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%; height:19px'}))

    # Request - what request each invocation builds. Query string, path params and headers
    # are edited as rows of widgets and serialized to JSON into these hidden fields
    # before the form is submitted.
    request_method = forms.CharField(required=False, initial='POST', widget=forms.TextInput(attrs={'style':'width:20%'}))
    request_query_string = forms.CharField(required=False, widget=forms.HiddenInput())
    request_path_params = forms.CharField(required=False, widget=forms.HiddenInput())
    request_headers = forms.CharField(required=False, widget=forms.HiddenInput())
    request_data = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%; height:4rem'}))
    request_data_mode = forms.ChoiceField(required=False, widget=forms.Select())

    # Response - how to transform the response before the callback receives it
    response_map = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%; height:4rem'}))
    response_map_mode = forms.ChoiceField(required=False, widget=forms.Select())

    # Callback - where to deliver the response
    callback_type = forms.ChoiceField(required=False, widget=forms.Select())
    callback_service = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    callback_topic = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    callback_rest = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))

    # Scheduler - the ID of the linked job, if any
    scheduler_job_id = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, security_list=None, soap_versions=SOAP_VERSIONS,
            prefix=None, post_data=None, req=None):

        security_list = security_list or []

        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['url_params_pri'].choices = []
        for value, label in url_params_priority:
            self.fields['url_params_pri'].choices.append([value, label])

        self.fields['params_pri'].choices = []
        for value, label in params_priority:
            self.fields['params_pri'].choices.append([value, label])

        self.fields['serialization_type'].initial = 'string'

        self.fields['soap_version'].choices = []
        for name in sorted(soap_versions):
            self.fields['soap_version'].choices.append([name, name])

        self.fields['validate_tls'].choices = []
        for value, label in validate_tls_choices:
            self.fields['validate_tls'].choices.append([value, label])

        self.fields['ping_method'].initial = DEFAULT_HTTP_PING_METHOD
        self.fields['pool_size'].initial = DEFAULT_HTTP_POOL_SIZE

        self.fields['scheduler_run_unit'].choices = []
        for value, label in scheduler_run_unit_choices:
            self.fields['scheduler_run_unit'].choices.append([value, label])

        self.fields['callback_type'].choices = []
        for value, label in callback_type_choices:
            self.fields['callback_type'].choices.append([value, label])

        self.fields['request_data_mode'].choices = []
        for value, label in request_value_mode_choices:
            self.fields['request_data_mode'].choices.append([value, label])

        self.fields['response_map_mode'].choices = []
        for value, label in response_map_mode_choices:
            self.fields['response_map_mode'].choices.append([value, label])

        # The generic health check tab shares its fields across connection types
        add_health_check_fields(self)

        add_security_select(self, security_list)

        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    match_slash = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################

class SearchForm(_ChooseClusterForm):
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, clusters, data=None):
        super(SearchForm, self).__init__(clusters, data)

        self.initial['connection'] = data.get('connection') or ''
        self.initial['transport'] = data.get('transport') or ''

# ################################################################################################################################
# ################################################################################################################################
