# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.urls import path

# Zato
from zato.rule_engine_dashboard.app.views import auth, events, users

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [

    # Sign-in and sign-out
    path('login/', auth.login, name='login'),
    path('login/callback/', auth.login_callback, name='login-callback'),
    path('logout/', auth.logout, name='logout'),

    # User management
    path('users/', users.users_list, name='users'),
    path('users/create', users.user_create, name='user-create'),
    path('users/<str:username>/edit', users.user_edit, name='user-edit'),
    path('users/<str:username>/change-password', users.user_change_password, name='user-change-password'),
    path('users/<str:username>/enable', users.user_set_active, {'is_active': True}, name='user-enable'),
    path('users/<str:username>/disable', users.user_set_active, {'is_active': False}, name='user-disable'),
    path('users/<str:username>/delete', users.user_delete, name='user-delete'),

    # One's own account
    path('profile/', users.profile, name='profile'),

    # The event trail
    path('events/', events.events_list, name='events'),
]

# ################################################################################################################################
# ################################################################################################################################
