# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.sample.protocol import as2, as4, ebxml
from zato.common.b2b.portal.sample.protocol.common import Protocol

# ################################################################################################################################
# ################################################################################################################################

Views_By_Protocol = {
    Protocol.ebXML: ebxml.Views,
    Protocol.AS2:   as2.Views,
    Protocol.AS4:   as4.Views,
}

# ################################################################################################################################
# ################################################################################################################################
