# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select, add_select_from_service, add_services, add_topics
from zato.common import FILE_TRANSFER, GENERIC

# ################################################################################################################################

_default = FILE_TRANSFER.DEFAULT
_source_type = FILE_TRANSFER.SOURCE_TYPE()
_sftp = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP

# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    service_list = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:87%', 'class':'multirow'}))
    topic_list = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:87%', 'class':'multirow'}))

    pickup_from = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    move_processed_to = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    file_patterns = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.FILE_PATTERNS)
    parse_with = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    read_on_pickup = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    parse_on_pickup = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    delete_after_pickup = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    source_type = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:15%'}))

    ftp_source_id = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:84%', 'class':'hidden'}))
    sftp_source_id = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:84%', 'class':'hidden'}))

    scheduler_job_id = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    line_by_line = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_select(self, 'source_type', _source_type)
        add_services(self, req)
        add_topics(self, req, by_id=False)
        add_select_from_service(self, req, 'zato.outgoing.ftp.get-list', 'ftp_source_id')
        add_select_from_service(self, req, 'zato.generic.connection.get-list', 'sftp_source_id', service_extra={'type_':_sftp})
        add_select_from_service(self, req, 'zato.scheduler.job.get-list', 'scheduler_job_id', service_extra={
            'service_name': FILE_TRANSFER.SCHEDULER_SERVICE
        })

# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    read_on_pickup = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    parse_on_pickup = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    delete_after_pickup = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
