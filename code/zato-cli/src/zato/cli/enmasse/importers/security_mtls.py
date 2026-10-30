# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import MTLS, SEC_DEF_TYPE

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

def prepare_mtls_definition(item:'anydict') -> 'None':
    """ Assigns the default use to an mTLS definition from YAML that does not name one, and refuses a use
    that does not exist as well as a field that does not apply to the use the definition names.
    """
    if item['type'] != SEC_DEF_TYPE.MTLS:
        return

    name = item['name']

    # A definition that does not say what it is used with is used with both sides ..
    if not (use_for := item.get(MTLS.Use_For_Field)):
        use_for = MTLS.Use_For.Default
        item[MTLS.Use_For_Field] = use_for

    # .. a use that does not exist is refused ..
    if use_for not in MTLS.Use_For_List:
        allowed = ', '.join(MTLS.Use_For_List)
        raise Exception(f'Security definition `{name}` -> invalid use_for `{use_for}`, expected one of: {allowed}')

    # .. and so is a field that the definition's use never reads, which is stored empty,
    # the same way the Dashboard stores it, so that an update clears what an earlier use left behind.
    for field in MTLS.Not_Applicable_Fields[use_for]:
        if item.get(field):
            raise Exception(f'Security definition `{name}` -> `{field}` does not apply to use_for `{use_for}`')
        item[field] = ''

# ################################################################################################################################
# ################################################################################################################################

def set_stored_use_for(item:'anydict') -> 'None':
    """ Assigns the default use to an mTLS definition read from the database that was stored without one,
    so that it is compared with YAML input as the definition it is at runtime.
    """
    if item['type'] != SEC_DEF_TYPE.MTLS:
        return

    if not item.get(MTLS.Use_For_Field):
        item[MTLS.Use_For_Field] = MTLS.Use_For.Default

# ################################################################################################################################
# ################################################################################################################################
