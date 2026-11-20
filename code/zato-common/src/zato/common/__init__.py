# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from importlib import import_module

# Re-exported for backward compatibility
from zato.common.api import *    # noqa: F401, F403

# Re-exported so that user code imports them from one place
from zato.common.util.message import Message as Message              # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.soap.message import SOAPMessage as SOAPMessage
    from zato.common.typing_ import any_
    from zato.common.util.xml_.message import XMLMessage as XMLMessage

# ################################################################################################################################
# ################################################################################################################################

# Re-exported so that user code imports them from one place as well, each from its module on first access,
# because these modules import lxml and cryptography, which commands of the CLI do not use.
_lazy_exports = {
    'SOAPMessage': 'zato.common.soap.message',
    'XMLMessage':  'zato.common.util.xml_.message',
}

# ################################################################################################################################
# ################################################################################################################################

def __getattr__(name:'str') -> 'any_':

    # Any other name is one that this package does not have ..
    if name not in _lazy_exports:
        raise AttributeError(f'Module `{__name__}` has no attribute `{name}`')

    # .. whereas a re-exported class is imported from its module.
    module = import_module(_lazy_exports[name])
    out = getattr(module, name)

    return out

# ################################################################################################################################
# ################################################################################################################################
