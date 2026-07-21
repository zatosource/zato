# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from contextlib import closing
from http.client import OK

# Zato
from zato.common.api import AS2, CONNECTION, URL_TYPE
from zato.common.as2.reconcile import MDNReconciler, process_incoming_mdn
from zato.common.ext_db.api import is_ext_db_configured, to_public_id
from zato.common.odb.model import HTTPSOAP
from zato.common.util.sql import parse_instance_opaque_attr
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AS2MDNEndpoint(AdminService):
    """ Built-in service that receives asynchronously delivered AS2 MDNs and matches them
    to previously sent messages through the reconciliation store. The endpoint always
    answers 200 with an empty body - the MDN's meaning is in its body, not the HTTP status -
    and an MDN for an unknown or already-reconciled Message-ID is accepted and logged,
    never errored.
    """

    name = 'zato.channel.as2.mdn.endpoint'

# ################################################################################################################################

    def handle(self) -> 'None':
        """ Processes one incoming asynchronous MDN.
        """

        # The MDN parser works with the raw wire bytes.
        body = self.request.raw

        if isinstance(body, str):
            body = body.encode('utf8')

        content_type = self.wsgi_environ.get('CONTENT_TYPE')
        if content_type is None:
            content_type = ''

        # Match the MDN against the sent messages - everything the reconciler learns
        # is recorded and logged inside, whether the MDN matched anything or not.
        reconciler = MDNReconciler(self.server.name)
        result = process_incoming_mdn(body, content_type, reconciler, cid=self.cid)

        if result.is_matched:
            logger.info('AS2 async MDN reconciled message `%s`, ok:%s; cid:%s',
                result.pending.message_id, result.is_ok, self.cid)

        # The answer is always a plain 200 with an empty body.
        self.response.status_code = OK
        self.response.payload = ''

# ################################################################################################################################
# ################################################################################################################################

class _KeystoreService(AdminService):
    """ Base class for services working with our own AS2 keystore, which lives
    on the inbound AS2 channel's row.
    """

    def _get_as2_channel(self, session:'any_') -> 'any_':
        """ Returns the inbound AS2 channel every server creates on startup.
        """
        out = session.query(HTTPSOAP).\
            filter(HTTPSOAP.name==AS2.Default.Channel_Name).\
            filter(HTTPSOAP.connection==CONNECTION.CHANNEL).\
            filter(HTTPSOAP.transport==URL_TYPE.AS2).\
            one()

        return out

# ################################################################################################################################
# ################################################################################################################################

class GetKeystore(_KeystoreService):
    """ Returns our own AS2 keystore - the signing pair, the current decryption key
    and the next decryption pair staged for rotation. Private keys come back
    the way they are stored, which is encrypted.
    """

    name = 'zato.channel.as2.keystore.get'

    output = ('id', 'name') + AS2.Keystore_Fields

    def handle(self) -> 'None':

        # The channel lives in the external AS2/AS4 database when one is configured.
        with closing(self.server.get_config_session(object_type=URL_TYPE.AS2)) as session:

            item = self._get_as2_channel(session)
            opaque = parse_instance_opaque_attr(item)

            self.response.payload.id = item.id
            self.response.payload.name = item.name

            # A fresh channel has no keystore yet, in which case each field is an empty string.
            for name in AS2.Keystore_Fields:
                value = opaque.get(name)
                if value is None:
                    value = ''
                setattr(self.response.payload, name, value)

# ################################################################################################################################
# ################################################################################################################################

class EditKeystore(_KeystoreService):
    """ Updates our own AS2 keystore on the inbound AS2 channel. The keystore fields
    are taken from input as given - an empty string clears a field, which is how
    the next decryption pair is removed once its rotation completes. All the other
    AS2 fields are carried over from the channel so they survive the edit.
    """

    name = 'zato.channel.as2.keystore.edit'

    input = tuple('-' + name for name in AS2.Keystore_Fields)
    output = '-id', '-name'

    def handle(self) -> 'None':

        input = self.request.input

        # The channel lives in the external AS2/AS4 database when one is configured.
        with closing(self.server.get_config_session(object_type=URL_TYPE.AS2)) as session:

            item = self._get_as2_channel(session)
            opaque = parse_instance_opaque_attr(item)

            item_id = item.id
            item_name = item.name
            item_url_path = item.url_path
            item_is_active = item.is_active

        # Everyone outside the external database knows the channel under its offset id.
        if is_ext_db_configured():
            item_id = to_public_id(item_id)

        # The edit service expects the full set of AS2 fields - the ones being edited
        # come from our input and the rest is carried over from the channel,
        # otherwise the edit would wipe them out.
        request = {
            'id': item_id,
            'name': item_name,
            'url_path': item_url_path,
            'is_active': item_is_active,
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.AS2,
            'cluster_id': self.server.cluster_id,
        }

        for name in AS2.Common_Fields + AS2.Channel_Fields:

            if name in AS2.Keystore_Fields:
                value = input[name]
            else:
                value = opaque.get(name)
                if value is None:
                    value = ''

            request[name] = value

        # The edit service encrypts the private keys, persists everything
        # and notifies all the servers in the cluster.
        _ = self.invoke('zato.http-soap.edit', request)

        self.response.payload.id = item_id
        self.response.payload.name = item_name

# ################################################################################################################################
# ################################################################################################################################
