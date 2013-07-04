# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import Logger

# Zato
from zato.common.log_message import NULL_LMC, NULL_CID

def wrapper(name):
    def _log(self, msg, *args, **kwargs):
        def _invoke(name, self, msg):
            extra={'cid':kwargs.pop('cid', NULL_CID), 'lmc':kwargs.pop('lmc', NULL_LMC)}
            extra.update(kwargs.pop('extra', {}))
            return Logger.__dict__[name](self, msg, *args, extra=extra, **kwargs)
        return _invoke(name, self, msg)
    return _log

class ZatoLogger(Logger):
    """ A custom subclass which turns parameters not understood otherwise
    into an 'extra' dictionary passed on to the base class.
    """
    debug = wrapper('debug')
    info = wrapper('info')
    warning = wrapper('warning')
    error = wrapper('error')
    
    # Alias
    warn = warning
