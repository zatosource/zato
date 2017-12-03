# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import CONNECTION, PUBSUB, URL_TYPE
from zato.admin.web.forms import add_http_soap_select, add_select, add_select_from_service

skip_endpoint_types = (
    PUBSUB.ENDPOINT_TYPE.IMAP.id,
    PUBSUB.ENDPOINT_TYPE.SQL.id,
    PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id,
)

# ################################################################################################################################

class CreateForm(forms.Form):

    id = forms.CharField(widget=forms.HiddenInput())
    server_id = forms.ChoiceField(widget=forms.Select())
    endpoint_type = forms.ChoiceField(widget=forms.Select())
    endpoint_id = forms.ChoiceField(widget=forms.Select())

    hook_serice_id = forms.ChoiceField(widget=forms.Select())

    active_status = forms.ChoiceField(widget=forms.Select())
    has_gd = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_staging_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    delivery_batch_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))
    wrap_one_msg_in_list = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    delivery_max_retry = forms.CharField(widget=forms.TextInput(attrs={'style':'width:25%'}))
    delivery_err_should_block = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    wait_sock_err = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))
    wait_non_sock_err = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))

    delivery_method = forms.ChoiceField(widget=forms.Select())
    delivery_data_format = forms.ChoiceField(widget=forms.Select())

    # This is not shown to users - only holds ID of an underlying interval-based job,
    # if one is in use for a given subscription.
    out_job_id = forms.CharField(widget=forms.HiddenInput())

    # REST
    rest_delivery_endpoint = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    out_rest_http_soap_id = forms.ChoiceField(widget=forms.Select())

    # SOAP
    soap_delivery_endpoint = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    out_soap_http_soap_id = forms.ChoiceField(widget=forms.Select())

    # Service
    service_id = forms.ChoiceField(widget=forms.Select())

    # WebSockets
    ws_channel_id = forms.ChoiceField(widget=forms.Select())

    # AMQP
    out_amqp_id = forms.ChoiceField(widget=forms.Select())
    amqp_exchange = forms.CharField(widget=forms.TextInput(attrs={'style':'width:49%'}))
    amqp_routing_key = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))

    # Flat files
    files_directory_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:60px'}))

    # FTP
    ftp_directory_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:60px'}))

    # SMTP - Twilio
    sms_twilio_from = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    sms_twilio_to_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:60px'}))

    # SMTP
    out_smtp_id = forms.ChoiceField(widget=forms.Select())
    smtp_subject = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    smtp_from = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    smtp_to_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:60px'}))
    smtp_body = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:120px'}))
    smtp_is_html = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    topic_list_text = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:120px'}))
    topic_list_json = forms.CharField(widget=forms.Textarea(attrs={'display':'none'}))

    def __init__(self, req, data_list, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

        add_select(self, 'endpoint_type', PUBSUB.ENDPOINT_TYPE, needs_initial_select=False, skip=skip_endpoint_types)
        add_select(self, 'service_id', data_list.service_list)

        add_select(self, 'active_status', PUBSUB.QUEUE_ACTIVE_STATUS)
        add_select(self, 'delivery_method', PUBSUB.DELIVERY_METHOD)
        add_select(self, 'delivery_data_format', PUBSUB.DATA_FORMAT)

        add_http_soap_select(self, 'out_rest_http_soap_id', req, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP)
        add_http_soap_select(self, 'out_soap_http_soap_id', req, CONNECTION.OUTGOING, URL_TYPE.SOAP)

        add_select_from_service(self, req, 'zato.server.get-list', 'server_id')

        self.initial['endpoint_type'] = PUBSUB.ENDPOINT_TYPE.REST.id
        self.initial['delivery_batch_size'] = PUBSUB.DEFAULT.DELIVERY_BATCH_SIZE
        self.initial['delivery_max_retry'] = PUBSUB.DEFAULT.DELIVERY_MAX_RETRY
        self.initial['wait_sock_err'] = PUBSUB.DEFAULT.WAIT_TIME_SOCKET_ERROR
        self.initial['wait_non_sock_err'] = PUBSUB.DEFAULT.WAIT_TIME_NON_SOCKET_ERROR



# ################################################################################################################################

class EditForm(CreateForm):
    pass

# ################################################################################################################################
