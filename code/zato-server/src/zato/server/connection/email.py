# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from cStringIO import StringIO
from logging import getLogger
from traceback import format_exc

# Outbox
from outbox import Outbox

# Zato
from zato.common import EMAIL
from zato.server.store import BaseAPI, BaseStore

logger = getLogger(__name__)

_modes = {
    EMAIL.SMTP.MODE.PLAIN.value: None,
    EMAIL.SMTP.MODE.SSL.value: 'SSL',
    EMAIL.SMTP.MODE.STARTTLS.value: 'TLS'
}

class EMailAPI(object):
    def __init__(self, smtp):
        self.smtp = smtp

class SMTPConnection(object):
    def __init__(self, config, config_no_sensitive):
        self.config = config
        self.config_no_sensitive = config_no_sensitive

    def __repr__(self):
        return '<{} at {}, config:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.config_no_sensitive)

    def send(self, email, *attachments):
        try:
            with Outbox(self.config.username, self.config.password, self.config.host, self.config.port, self.config.mode_outbox,
                    self.config.is_debug) as conn:
                conn.send(email, attachments)
        except Exception, e:
            logger.warn('Could not send an SMTP message to `%s`, e:`%s`', self.config_no_sensitive, format_exc(e))

class SMTPAPI(BaseAPI):
    """ API to obtain SMTP connections through.
    """

class SMTPConnStore(BaseStore):
    """ Stores connections to SMTP.
    """
    def create_impl(self, config, config_no_sensitive):
        #return get_es(config.hosts.splitlines(), float(config.timeout), send_get_body_as=config.body_as)
        config.mode_outbox = _modes[config.mode]
        return SMTPConnection(config, config_no_sensitive)
