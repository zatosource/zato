# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

'''
# stdlib
from logging import getLogger

# Boto
from boto3.s3.bucket import Bucket
from boto3.s3.connection import NoHostProvided, S3Connection
from boto3.s3.key import Key

# Zato
from zato.common.api import ZATO_NONE
from zato.common.util.api import parse_extra_into_dict
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class _S3Connection:
    def __init__(self, **kwargs):
        self.zato_default_bucket = kwargs.pop('bucket')
        self.zato_content_type = kwargs.pop('content_type')
        self.zato_metadata = kwargs.pop('metadata')

        encrypt_at_rest = kwargs.pop('encrypt_at_rest')
        self.zato_encrypt_at_rest = 'AES256' if encrypt_at_rest else None

        self.zato_storage_class = kwargs.pop('storage_class')
        self.impl = S3Connection(**kwargs)

    def check_connection(self):
        self.impl.get_canonical_user_id()

    def set(self, key, value, bucket=ZATO_NONE, content_type=ZATO_NONE, metadata=ZATO_NONE,
            storage_class=ZATO_NONE, encrypt_at_rest=ZATO_NONE):
        _bucket = Bucket(self.impl, bucket if bucket != ZATO_NONE else self.zato_default_bucket)
        _key = Key(_bucket)

        _key.content_type = content_type if content_type != ZATO_NONE else self.zato_content_type
        _key.metadata.update(metadata if metadata != ZATO_NONE else parse_extra_into_dict(self.zato_metadata, False))
        _key.name = key
        _key.storage_class = storage_class if storage_class != ZATO_NONE else self.zato_storage_class
        _key.set_contents_from_string(
            value, encrypt_key=(encrypt_at_rest if encrypt_at_rest != ZATO_NONE else self.zato_encrypt_at_rest))

# ################################################################################################################################
# ################################################################################################################################

class S3Wrapper(Wrapper):
    """ Wraps a queue of connections to AWS S3.
    """
    def __init__(self, config, server):
        config.auth_url = config.address
        super(S3Wrapper, self).__init__(config, 'AWS S3', server)

    def add_client(self):
        conn = _S3Connection(aws_access_key_id=self.config.username, aws_secret_access_key=self.config.password,
            debug=self.config.debug_level,
            suppress_consec_slashes=self.config.suppr_cons_slashes, content_type=self.config.content_type,
            metadata=self.config.metadata_ or {}, bucket=self.config.bucket, encrypt_at_rest=self.config.encrypt_at_rest,
            storage_class=self.config.storage_class, host=self.server.fs_server_config.misc.aws_host or NoHostProvided)

        # Sanity check - no exception here means the config is correct.
        conn.check_connection()

        self.client.put_client(conn)

# ################################################################################################################################
# ################################################################################################################################
'''
