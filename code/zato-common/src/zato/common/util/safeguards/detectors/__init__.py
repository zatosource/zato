# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex import detectors as piigex_detectors

# Zato - importing a land module registers its detectors with the underlying library's registry,
# and the secrets module registers the credential detectors the same way.
from zato.common.util.safeguards.detectors import au, br, ca, ee, fi, in_, intl, is_, jp, kr, lu, mx, no, nz, ph, secrets, sg, za

# For flake8
au   = au
br   = br
ca   = ca
ee   = ee
fi   = fi
in_  = in_
intl = intl
is_  = is_
jp   = jp
kr   = kr
lu   = lu
mx   = mx
no   = no
nz   = nz
ph   = ph
secrets = secrets
sg   = sg
za   = za

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The prefixes the underlying library gives its international detectors and their tokens -
# they never appear in anything user-facing.
_library_prefix       = 'intl_'
_library_token_prefix = 'INTL_'

# The phone detector is named after what it finds, not after the notation its pattern implements.
_phone_library_name = 'intl_phone_e164'
_phone_public_name  = 'phone_number'
_phone_public_token = 'PHONE_NUMBER'

# ################################################################################################################################
# ################################################################################################################################

def _rename_international_detectors() -> 'None':
    """ Gives the library's international detectors their public names - the intl_ prefix
    stays internal to the library and every name Zato exposes is without it.
    """
    registry = piigex_detectors.get_registry()

    # Collect the prefixed names first - the registry itself changes below.
    prefixed_names:'strlist' = []

    for name in registry:
        if name.startswith(_library_prefix):
            prefixed_names.append(name)

    for name in prefixed_names:

        detector = registry[name]

        # The phone detector has a full rename of its own ..
        if name == _phone_library_name:
            new_name = _phone_public_name
            new_token = _phone_public_token

        # .. every other detector just loses the prefix, in its token too when it carries one.
        else:
            new_name = name.removeprefix(_library_prefix)
            new_token = detector.token.removeprefix(_library_token_prefix)

        detector.name = new_name
        detector.token = new_token

        # Re-register under the public name and drop the prefixed key -
        # the library has no removal call, so its registry is reached into directly.
        piigex_detectors.register(detector)
        del piigex_detectors._REGISTRY[name]

# ################################################################################################################################

_rename_international_detectors()

# ################################################################################################################################
# ################################################################################################################################
