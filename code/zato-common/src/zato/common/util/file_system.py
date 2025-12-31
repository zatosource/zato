# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import re
import string
from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path
from tempfile import gettempdir
from time import sleep
from uuid import uuid4

# Zato
from zato.common.util.time_ import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, dictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

_re_fs_safe_name = '[{}]'.format(string.punctuation + string.whitespace)

# ################################################################################################################################

def fs_safe_name(value:'str') -> 'str':
    return re.sub(_re_fs_safe_name, '_', value)

# ################################################################################################################################

def fs_safe_now(_utcnow:'callable_'=utcnow) -> 'str':
    """ Returns a UTC timestamp with any characters unsafe for filesystem names removed.
    """
    return fs_safe_name(_utcnow().isoformat())

# ################################################################################################################################

def wait_for_file(path:'str', max_wait:'int'=5) -> 'None':

    found = False
    now   = utcnow()
    until = now + timedelta(seconds=max_wait)

    while now < until:
        if os.path.exists(path):
            found = True
            break
        else:
            sleep(0.05)
            now = utcnow()

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

def resolve_path(path:'str', base_dir:'str'='') -> 'str':

    # Local aliases
    has_env  = '$' in path
    has_home = '~' in path
    is_relative = not os.path.isabs(path)

    # We can return the path as is if there is nothing to resolve
    if not (has_env or has_home or is_relative):
        return path

    # Expand the path to the user's directory first ..
    if has_home:
        path = os.path.expanduser(path)

    # .. we can expand environment variables too ..
    if has_env:
        path = os.path.expandvars(path)

    # .. if what we have is not an absolute path, it means that we need to turn it into one ..
    # .. while keeping it mind that it is relative to the base directory that we have on input ..
    if not os.path.isabs(path):
        path = os.path.join(base_dir, path)
        path = os.path.abspath(path)

    # .. now, we can return the result to our caller ..
    return path

# ################################################################################################################################

def touch(path:'str') -> 'None':
    Path(path).touch()

# ################################################################################################################################

def touch_multiple(path_list:'strlist') -> 'None':
    for path in path_list:
        touch(path)

# ################################################################################################################################

def _walk_python_files(root_dir: 'str'):
    for root, _, files in os.walk(root_dir):
        for item in files:
            if item.endswith('.py'):
                yield os.path.join(root, item)

# ################################################################################################################################

def touch_python_files(root_dir:'str') -> 'None':
    for full_path in _walk_python_files(root_dir):
        try:
            touch(full_path)
        except Exception as e:
            logger.warning('Could not touch %s -> %s', full_path, e)

# ################################################################################################################################

def get_python_files(root_dir:'str') -> 'dictlist':
    results = []
    for full_path in _walk_python_files(root_dir):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = f.read()
            results.append({'full_path': full_path, 'data': data})
        except Exception as e:
            logger.warning('Could not read %s -> %s', full_path, e)
    return results

# ################################################################################################################################
