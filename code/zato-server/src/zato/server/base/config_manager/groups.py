# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import Groups
from zato.server.base.config_manager.common import ConfigManagerImpl

logger_groups = logging.getLogger('zato.groups.config_manager')

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_
    from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroups(ConfigManagerImpl):
    """ Security groups-related functionality for config manager objects.
    """

# ################################################################################################################################

    def _yield_security_groups_ctx_items(
        self:'ConfigManager' # type: ignore
    ) -> 'any_':

        for channel_item in self.config_store.http_soap:
            if security_groups_ctx := channel_item.get('security_groups_ctx'):
                yield security_groups_ctx

# ################################################################################################################################

    def on_config_event_Groups_Edit(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':
        logger_groups.info('on_config_event_Groups_Edit: msg=%s', msg)

# ################################################################################################################################

    def on_config_event_Groups_Edit_Member_List(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

        logger_groups.info('on_config_event_Groups_Edit_Member_List: msg=%s', msg)

        member_id_list = msg.member_id_list
        member_id_list = [elem.split('-') for elem in member_id_list]
        member_id_list = [elem[1] for elem in member_id_list]
        member_id_list = [int(elem) for elem in member_id_list]

        for security_groups_ctx in self._yield_security_groups_ctx_items():

            if msg.group_action == Groups.Membership_Action.Add:
                func = security_groups_ctx.on_member_added_to_group
            else:
                func = security_groups_ctx.on_member_removed_from_group

            for member_id in member_id_list:
                func(msg.group_id, member_id)

# ################################################################################################################################

    def on_config_event_Groups_Delete(
        self:'ConfigManager', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

        for security_groups_ctx in self._yield_security_groups_ctx_items():
            security_groups_ctx.on_group_deleted(msg.id)

# ################################################################################################################################
# ################################################################################################################################
