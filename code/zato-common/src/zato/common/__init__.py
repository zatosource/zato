# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Re-exported for backward compatibility
from zato.common.api import *    # noqa: F401, F403

# Re-exported so that user code imports them from one place
from zato.common.util.message import Message as Message              # noqa: F401
from zato.common.util.xml_.message import XMLMessage as XMLMessage   # noqa: F401
from zato.common.soap.message import SOAPMessage as SOAPMessage      # noqa: F401
