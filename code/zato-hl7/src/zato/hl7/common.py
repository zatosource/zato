# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class Const:
    """ Various HL7-related constants.
    """
    class Version:

        # A generic v2 message, without an indication of a specific release.
        v2 = 'v2'

    class ImplClass:
        hl7apy = 'hl7apy'
        zato   = 'Zato'

impl_class_all     = {Const.ImplClass.hl7apy, Const.ImplClass.zato}
impl_class_current = {Const.ImplClass.hl7apy}

# ################################################################################################################################
# ################################################################################################################################
