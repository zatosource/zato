# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class AuditSuite:
    """ The collector of the suite, which the conftest starts before the server and the tests read the records of.
    """

    # The file to which the collector writes each record that the workers export
    collector_output_path = ''

# ################################################################################################################################
# ################################################################################################################################
