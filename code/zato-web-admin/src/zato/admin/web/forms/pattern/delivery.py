# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter

# Django
from django import forms

# Zato
from zato.admin.web.forms import INITIAL_CHOICES_DICT
from zato.common import INVOCATION_TARGET

_targets = {
    INVOCATION_TARGET.CHANNEL_AMQP: 'Channel - AMQP',
    INVOCATION_TARGET.CHANNEL_WMQ: 'Channel - WebSphere MQ',
    INVOCATION_TARGET.CHANNEL_ZMQ: 'Channel - ZeroMQ',
    INVOCATION_TARGET.OUTCONN_AMQP: 'Outgoing conn. - AMQP',
    INVOCATION_TARGET.OUTCONN_WMQ: 'Outgoing conn. - WebSphere MQ',
    INVOCATION_TARGET.OUTCONN_ZMQ: 'Outgoing conn. - ZeroMQ',
    INVOCATION_TARGET.SERVICE: 'Service',
}
_targets.update(INITIAL_CHOICES_DICT)

class DeliveryTargetForm(forms.Form):
    target_type = forms.ChoiceField(widget=forms.Select())

    def __init__(self, data=None):
        super(DeliveryTargetForm, self).__init__(data)
        self.fields['target_type'].choices = []
        for id, name in sorted(_targets.iteritems(), key=itemgetter(1)):
            self.fields['target_type'].choices.append([id, name])
            
class CreateForm(forms.Form):
    pass

class EditForm(forms.Form):
    pass