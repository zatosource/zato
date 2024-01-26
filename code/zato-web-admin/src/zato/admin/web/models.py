# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django.db import models
from django.contrib.auth.models import User

# Zato
from zato.admin.web import DATE_FORMATS, MONTH_YEAR_FORMATS, TIME_FORMATS
from zato.common.json_internal import loads

# Not used in practice
def _on_delete(*unused_args, **unused_kwargs):
    pass

class TOTPData:
    def __init__(self):
        self.key = None
        self.label = None

class UserProfile(models.Model):
    class Meta:
        db_table = 'user_profile'

    user = models.OneToOneField(User, on_delete=_on_delete)
    timezone = models.CharField(max_length=100, null=True, default='UTC')
    date_format = models.CharField(max_length=100, null=True, default='dd-mm-yyyy')
    time_format = models.CharField(max_length=10, null=True, default='24')
    opaque1 = models.TextField(null=True)

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.date_format_py = DATE_FORMATS[self.date_format]
        self.time_format_py = TIME_FORMATS[self.time_format]
        self.month_year_format_py = MONTH_YEAR_FORMATS[self.date_format]
        self.month_year_format_strptime = self.month_year_format_py.replace('m', '%m').replace('y', '%y').replace('Y', '%Y')
        self.year_format_py = 'Y'
        self.date_time_format_py = '{} {}'.format(self.date_format_py, self.time_format_py)

    def __repr__(self):
        return '<{} at {} user:[{}] timezone:[{}] date_format_py:[{}] time_format_py:[{}] month_year_format_py:[{}] date_time_format_py:[{}]>'.format(
            self.__class__.__name__, hex(id(self)), self.user, self.timezone, self.date_format_py,
            self.time_format_py, self.month_year_format_py, self.date_time_format_py)

    __unicode__ = __repr__

    def get_totp_data(self):
        totp_data = TOTPData()

        if self.opaque1:
            opaque = loads(self.opaque1)
            totp_data.key = opaque.get('totp_key')
            totp_data.label = opaque.get('totp_label')

        return totp_data

class ClusterColorMarker(models.Model):
    class Meta:
        db_table = 'cluster_color_marker'

    user_profile = models.ForeignKey(UserProfile, on_delete=_on_delete, related_name='cluster_color_markers')
    cluster_id = models.IntegerField()
    color = models.CharField(max_length=6) # RGB

    def __repr__(self):
        return '<{} at {} user_profile:[{}] cluster_id:[{}] color:[{}]>'.format(
            self.__class__.__name__, hex(id(self)), self.user_profile, self.cluster_id, self.color)

    __unicode__ = __repr__
