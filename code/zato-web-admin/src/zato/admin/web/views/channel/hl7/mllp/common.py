# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.admin.web import alerts_tab
from zato.common.alerting.object_config import alert_type_mllp_channel
from zato.common.api import Groups, SEC_DEF_TYPE
from zato.common.hl7.mllp.fields import Matcher_Labels

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato.admin.web.views.channel.hl7.mllp')

# .. name prefix for backing REST channels ..
_REST_Channel_Name_Prefix = 'hl7.rest.'

# .. the multi-step wizard template, serving both the create and the edit page ..
_Wizard_Template = 'zato/channel/hl7/mllp-wizard.html'

# .. the alert settings a channel carries and the names they travel under between the wizard and the backend ..
_alert_type = alert_type_mllp_channel
_alert_field_names = alerts_tab.get_storage_field_names(_alert_type)

# .. what the security selects carry in front of a definition's id, an id alone being
# .. what a channel stores under security_id ..
_MTLS_Select_Prefix = SEC_DEF_TYPE.MTLS + '/'

# .. the two flags a row turns over on the list itself ..
_Inline_Flag_Names = ['is_active', 'is_default']

# .. what a message is handed to, which the list edits in the wizard's own panels ..
_Inline_Target_Names = ['service', 'destinations', 'respond_from', 'delivery_mode']

# .. everything a row may change without the wizard being opened ..
_Inline_Field_Names = [name for name, _ in Matcher_Labels] + _Inline_Flag_Names + _Inline_Target_Names

# .. what the page is told when no other channel held the default flag ..
_No_Previous_Default = 0

# .. and what the fields a row is edited through are named after.
_Row_Edit_Prefix = 'mllp-row'

# ################################################################################################################################
# ################################################################################################################################

def _get_security_group_id(req:'any_', group_name:'str') -> 'int':
    """ Returns the id of the API client group of this name, zero when there is none.
    """
    response = req.zato.client.invoke('zato.groups.get-list', {
        'group_type': Groups.Type.API_Clients,
    })

    for group in response.data:
        if group['name'] == group_name:
            out = group['id']
            break
    else:
        out = 0

    return out

# ################################################################################################################################
# ################################################################################################################################
