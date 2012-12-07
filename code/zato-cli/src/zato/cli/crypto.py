# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# Zato
from zato.cli import ZatoCommand
from zato.common.crypto import CryptoManager
from zato.common.util import decrypt, encrypt

class Encrypt(ZatoCommand):
    """ Encrypts secrets using a public key
    """
    allow_empty_secrets = True
    opts = [{'name':'--secret', 'help':'Secret to encrypt'}]
    
    def execute(self, args):
        cm = CryptoManager(pub_key_location=os.path.abspath(args.path))
        cm.load_keys()
        
        self.logger.info('Encrypted value is [{}]'.format(cm.encrypt(args.secret)))
    
class Decrypt(ZatoCommand):
    """ Decrypts secrets using a private key
    """
    allow_empty_secrets = True
    opts = [{'name':'--secret', 'help':'Secret to decrypt'}]
    
    def execute(self, args):
        cm = CryptoManager(priv_key_location=os.path.abspath(args.path))
        cm.load_keys()
        
        self.logger.info('Secret is [{}]'.format(cm.decrypt(args.secret)))