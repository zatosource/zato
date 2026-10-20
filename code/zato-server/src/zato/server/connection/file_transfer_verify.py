# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.file_transfer.api import VerifyHow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, stranydict
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

class FileTransferVerifyError(Exception):
    """ Raised when the remote copy of a stored file does not match the bytes that were sent.
    """

# ################################################################################################################################
# ################################################################################################################################

def verify_store(
    get_remote_size:'callable_',
    get_remote_checksum:'callable_',
    remote_path:'str',
    size:'int',
    checksum:'str',
    verify_how:'str',
    ) -> 'stranydict':
    """ Compares a stored file with the bytes sent, by size or by read-back checksum, and returns the result.
    """

    # Our response to produce
    out:'stranydict' = {
        'verify_how': verify_how,
        'mismatch': '',
    }

    # The remote size is what every check starts with ..
    remote_size = get_remote_size(remote_path)
    out['remote_size'] = remote_size

    if remote_size != size:
        out['mismatch'] = f'Remote size is {remote_size} instead of {size} for `{remote_path}`'
        return out

    # .. and a read-back check compares the checksum of the bytes read back one chunk at a time.
    if verify_how == VerifyHow.Read_Back:

        remote_checksum = get_remote_checksum(remote_path)
        out['remote_checksum'] = remote_checksum

        if remote_checksum != checksum:
            out['mismatch'] = f'Remote checksum is {remote_checksum} instead of {checksum} for `{remote_path}`'

    return out

# ################################################################################################################################
# ################################################################################################################################
