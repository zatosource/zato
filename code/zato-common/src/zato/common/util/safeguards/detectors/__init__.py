# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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
