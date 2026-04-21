# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.sql import get_instance_by_id, get_instance_by_name
from zato.server.service.internal import AdminService

# ################################################################################################################################

class _BaseService(AdminService):

# ################################################################################################################################

    def _get_instance_by_id(self, session, model_class, id):
        return get_instance_by_id(session, model_class, id)

# ################################################################################################################################

    def _get_instance_by_name(self, session, model_class, type_, name):
        return get_instance_by_name(session, model_class, type_, name)

# ################################################################################################################################
