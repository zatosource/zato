# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# Django
from django import forms

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems

# Zato
from zato.admin.web.forms import INITIAL_CHOICES_DICT
from zato.common.api import BATCH_DEFAULTS, INVOCATION_TARGET

# It's a pity these have to be repeated here in addition to what is in zato.admin.web
# but here the names are shorter.
_targets = {
    INVOCATION_TARGET.CHANNEL_AMQP: 'Channel - AMQP',
    INVOCATION_TARGET.CHANNEL_WMQ: 'Channel - IBM MQ',
    INVOCATION_TARGET.CHANNEL_ZMQ: 'Channel - ZeroMQ',
    INVOCATION_TARGET.OUTCONN_AMQP: 'Outgoing conn. - AMQP',
    INVOCATION_TARGET.OUTCONN_WMQ: 'Outgoing conn. - IBM MQ',
    INVOCATION_TARGET.OUTCONN_ZMQ: 'Outgoing conn. - ZeroMQ',
    INVOCATION_TARGET.SERVICE: 'Service',
}
_targets.update(INITIAL_CHOICES_DICT)

class DeliveryTargetForm(forms.Form):
    target_type = forms.ChoiceField(widget=forms.Select())

    def __init__(self, data=None):
        super(DeliveryTargetForm, self).__init__(data)
        self.fields['target_type'].choices = []
        for id, name in sorted(iteritems(_targets), key=itemgetter(1)):
            self.fields['target_type'].choices.append([id, name])

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    target = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    check_after = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:18%'}))
    retry_repeats = forms.CharField(initial=5, widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:12%'}))
    retry_seconds = forms.CharField(initial=600, widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:18%'}))

    expire_after = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:18%'}))
    expire_arch_succ_after = forms.CharField(initial=72, widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:12%'}))
    expire_arch_fail_after = forms.CharField(initial=168, widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:12%'}))

    callback_list = forms.CharField(widget=forms.Textarea(attrs={'rows':7}), required=False)

class EditForm(CreateForm):
    pass

class InstanceListForm(forms.Form):
    """ List of delivery instances.
    """
    start = forms.CharField(widget=forms.TextInput(attrs={'style':'width:150px; height:19px'}))
    stop = forms.CharField(widget=forms.TextInput(attrs={'style':'width:150px; height:19px'}))
    current_batch = forms.CharField(initial=BATCH_DEFAULTS.PAGE_NO, widget=forms.TextInput(attrs={'style':'width:50px; height:19px'}))
    batch_size = forms.CharField(initial=BATCH_DEFAULTS.SIZE, widget=forms.TextInput(attrs={'style':'width:50px; height:19px'}))
