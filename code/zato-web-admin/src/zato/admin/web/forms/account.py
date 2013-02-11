# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
