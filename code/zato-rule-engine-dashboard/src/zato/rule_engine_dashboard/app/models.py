# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.db import models
from django.utils import timezone

# ################################################################################################################################
# ################################################################################################################################

class UserAction:
    """ The actions the user event trail records.
    """
    Create          = 'user.create'
    Update          = 'user.update'
    Delete          = 'user.delete'
    Enable          = 'user.enable'
    Disable         = 'user.disable'
    Password_Change = 'user.password_change'

# ################################################################################################################################
# ################################################################################################################################

class UserEvent(models.Model):
    """ One user management action - who did what to whom, from where and when.
    """

    actor       = models.CharField(max_length=191)
    action      = models.CharField(max_length=64)
    subject     = models.CharField(max_length=191)
    remote_addr = models.CharField(max_length=191)
    details     = models.TextField()
    created_at  = models.DateTimeField(default=timezone.now, db_index=True)

    # Django adds the default manager dynamically, so it is declared here for the type checkers' sake
    objects = models.Manager()

    class Meta:
        app_label = 'rule_engine_dashboard'
        db_table = 'rule_user_event'

# ################################################################################################################################
# ################################################################################################################################

def add_event(actor:'str', action:'str', subject:'str', remote_addr:'str', details:'str') -> 'UserEvent':
    """ Appends one event to the trail - called in the same transaction as the change it describes.
    """
    out = UserEvent(
        actor=actor,
        action=action,
        subject=subject,
        remote_addr=remote_addr,
        details=details,
    )
    out.save()

    return out

# ################################################################################################################################
# ################################################################################################################################
