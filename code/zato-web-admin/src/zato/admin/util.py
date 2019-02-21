# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

def get_user_profile(req):
    try:
        user_profile = UserProfile.objects.get(user=req.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=req.user)
        user_profile.save()
