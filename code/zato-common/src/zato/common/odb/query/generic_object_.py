# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.odb.model import GenericObject

# ################################################################################################################################

def generic_object(session, cluster_id, type_, name):
    """ Generic objects by type and name.
    """
    return session.query(GenericObject).\
        filter(GenericObject.cluster_id==cluster_id).\
        filter(GenericObject.type_==type_).\
        filter(GenericObject.name==name)

# ################################################################################################################################
