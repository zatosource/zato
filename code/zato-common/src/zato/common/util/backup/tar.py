# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import io
import os
import tarfile

# Zato
from zato.common.util.backup.config import exclude_dirs, exclude_files

# ################################################################################################################################
# ################################################################################################################################

def _should_exclude(path:'str', relative_path:'str') -> 'bool':

    parts = relative_path.split(os.sep)

    for part in parts:
        if part in exclude_dirs:
            return True

    basename = os.path.basename(path)
    if basename in exclude_files:
        return True

    return False

# ################################################################################################################################

def create_tar_gz(env_dir:'str') -> 'bytes':
    buffer = io.BytesIO()

    with tarfile.open(fileobj=buffer, mode='w:gz') as tar:
        for dirpath, dirnames, filenames in os.walk(env_dir):

            relative_dir = os.path.relpath(dirpath, env_dir)
            if relative_dir == '.':
                relative_dir = ''

            if _should_exclude(dirpath, relative_dir):
                dirnames.clear()
                continue

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)

                if relative_dir:
                    relative_path = os.path.join(relative_dir, filename)
                else:
                    relative_path = filename

                if _should_exclude(full_path, relative_path):
                    continue

                tar.add(full_path, arcname=relative_path)

    out = buffer.getvalue()
    return out

# ################################################################################################################################
# ################################################################################################################################
