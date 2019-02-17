# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

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

        self.fields['timezone'].choices = ((item, item) for item in common_timezones)
        self.fields['date_format'].choices = ((item, item) for item in sorted(DATE_FORMATS))
        self.fields['time_format'].choices = ((item, '{}-hour'.format(item)) for item in sorted(TIME_FORMATS))
