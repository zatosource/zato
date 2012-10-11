# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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
from django.db import models
from django.contrib.auth.models import User

# Zato
from zato.admin.web import DATE_FORMATS, MONTH_YEAR_FORMATS, TIME_FORMATS

class UserProfile(models.Model):
    class Meta:
        db_table = 'user_profile'
        
    user = models.ForeignKey(User, unique=True)
    timezone = models.CharField(max_length=100, null=True, default='UTC')
    date_format = models.CharField(max_length=100, null=True, default='dd-mm-yyyy')
    time_format = models.CharField(max_length=10, null=True, default='24')
    
    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.date_format_py = DATE_FORMATS[self.date_format]
        self.time_format_py = TIME_FORMATS[self.time_format]
        self.month_year_format_py = MONTH_YEAR_FORMATS[self.date_format]
        self.date_time_format_py = '{} {}'.format(self.date_format_py, self.time_format_py)
    
    def __repr__(self):
        return '<{} at {} user:[{}] timezone:[{}] date_format_py:[{}] time_format_py:[{}] month_year_format_py:[{}] date_time_format_py:[{}]>'.format(
            self.__class__.__name__, hex(id(self)), self.user, self.timezone, self.date_format_py,
            self.time_format_py, self.month_year_format_py, self.date_time_format_py)
    
    __unicode__ = __repr__
    
class ClusterColorMarker(models.Model):
    class Meta:
        db_table = 'cluster_color_marker'
    
    user_profile = models.ForeignKey(UserProfile, related_name='cluster_color_markers')
    cluster_id = models.IntegerField()
    color = models.CharField(max_length=6) # RGB

    def __repr__(self):
        return '<{} at {} user_profile:[{}] cluster_id:[{}] color:[{}]>'.format(
            self.__class__.__name__, hex(id(self)), self.user_profile, self.cluster_id, self.color)
    
    __unicode__ = __repr__
