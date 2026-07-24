# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.urls import path

# Zato
from zato.rule_engine_dashboard.app import views

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('users/', views.users_list, name='users'),
    path('users/<str:username>/enable', views.user_set_active, {'is_active': True}, name='user-enable'),
    path('users/<str:username>/disable', views.user_set_active, {'is_active': False}, name='user-disable'),
    path('users/<str:username>/delete', views.user_delete, name='user-delete'),
]

# ################################################################################################################################
# ################################################################################################################################
