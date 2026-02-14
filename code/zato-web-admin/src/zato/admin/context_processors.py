# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from os import environ

def zato_env_name(request):
    return {
        'zato_env_name': environ.get('Zato_Env_Name', '')
    }
