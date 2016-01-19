# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# pytz
from pytz import common_timezones

# Zato
from zato.admin.web import DATE_FORMATS, TIME_FORMATS

class BasicSettingsForm(forms.Form):
    """ All the basic settings not including cluster color markers.
    """
    timezone = forms.ChoiceField()
    date_format = forms.ChoiceField()
    time_format = forms.ChoiceField()

    def __init__(self, initial, *args, **kwargs):
        super(BasicSettingsForm, self).__init__(initial, *args, **kwargs)

        for field in self.fields:
            self.fields[field].choices[:] = []

        for tz in common_timezones:
            self.fields['timezone'].choices.append([tz, tz])

        for item in sorted(DATE_FORMATS):
            self.fields['date_format'].choices.append([item, item])

        for item in sorted(TIME_FORMATS):
            self.fields['time_format'].choices.append([item, '{}-hour'.format(item)])
