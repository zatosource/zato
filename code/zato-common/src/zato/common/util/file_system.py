# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import string
from datetime import datetime, timedelta
from tempfile import gettempdir
from time import sleep
from uuid import uuid4

# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################

_re_fs_safe_name = '[{}]'.format(string.punctuation + string.whitespace)

# ################################################################################################################################

def fs_safe_name(value:'str') -> 'str':
    return re.sub(_re_fs_safe_name, '_', value)

# ################################################################################################################################

def fs_safe_now(_utcnow:'callable_'=datetime.utcnow) -> 'str':
    """ Returns a UTC timestamp with any characters unsafe for filesystem names removed.
    """
    return fs_safe_name(_utcnow().isoformat())

# ################################################################################################################################

def wait_for_file(path:'str', max_wait:'int'=5) -> 'None':

    found = False
    now   = datetime.utcnow()
    until = now + timedelta(seconds=max_wait)

    while now < until:
        found = os.path.exists(path)
        if found:
            break
        else:
            sleep(0.05)
            now = datetime.utcnow()

# ################################################################################################################################

def get_tmp_path(prefix:'str'='', body:'str'='', suffix:'str'='') -> 'str':

    tmp_dir = gettempdir()

    prefix = prefix or 'zato'
    body   = body   or uuid4().hex
    suffix = suffix or uuid4().hex

    file_name = f'{prefix}-{body}-{suffix}'
    tmp_path = os.path.join(tmp_dir, file_name)

    return tmp_path

# ################################################################################################################################
