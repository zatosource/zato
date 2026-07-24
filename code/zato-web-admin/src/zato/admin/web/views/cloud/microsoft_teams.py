# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web.views import method_allowed, ping_connection
from zato.admin.web.views.cloud import microsoft_365
from zato.common.api import GENERIC

# ################################################################################################################################
# ################################################################################################################################

class Index(microsoft_365.Index):
    url_name = 'chat-microsoft-teams'
    template = 'zato/cloud/microsoft-teams.html'

# ################################################################################################################################
# ################################################################################################################################

class Create(microsoft_365.Create):
    url_name = 'chat-microsoft-teams-create'
    conn_type = GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS
    conn_label = 'Microsoft Teams'

# ################################################################################################################################
# ################################################################################################################################

class Edit(microsoft_365.Edit):
    url_name = 'chat-microsoft-teams-edit'
    conn_type = GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS
    conn_label = 'Microsoft Teams'

# ################################################################################################################################
# ################################################################################################################################

class Delete(microsoft_365.Delete):
    url_name = 'chat-microsoft-teams-delete'
    error_message = 'Could not delete Microsoft Teams connection'

# ################################################################################################################################
# ################################################################################################################################

# The secret is updated through the same view as with Microsoft 365 connections.
change_password = microsoft_365.change_password

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    out = ping_connection(req, 'zato.generic.connection.ping', id, 'Microsoft Teams connection')
    return out

# ################################################################################################################################
# ################################################################################################################################
