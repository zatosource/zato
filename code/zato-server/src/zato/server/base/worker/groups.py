# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import Groups
from zato.server.base.worker.common import WorkerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from bunch import Bunch
    from zato.common.typing_ import any_
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

class SecurityGroups(WorkerImpl):
    """ Security groups-related functionality for worker objects.
    """

# ################################################################################################################################

    def _yield_security_groups_ctx_items(
        self:'WorkerStore' # type: ignore
    ) -> 'any_':

        for channel_item in self.worker_config.http_soap:
            if security_groups_ctx := channel_item.get('security_groups_ctx'):
                yield security_groups_ctx

# ################################################################################################################################

    def on_broker_msg_Groups_Edit_Member_List(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

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

    def on_broker_msg_Groups_Delete(
        self:'WorkerStore', # type: ignore
        msg, # type: Bunch
    ) -> 'None':

        for security_groups_ctx in self._yield_security_groups_ctx_items():
            security_groups_ctx.on_group_deleted(msg.id)

# ################################################################################################################################
# ################################################################################################################################
