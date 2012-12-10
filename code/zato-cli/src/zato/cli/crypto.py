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

# anyjson
import anyjson

# Zato
from zato.cli import ManageCommand, ZatoCommand
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
        
class UpdateCrypto(ManageCommand):
    """ Updates cryptographic material of a given Zato component
    """
    opts = [
        {'name':'priv_key_path', 'help':'Path to a private key in PEM'},
        {'name':'pub_key_path', 'help':'Path to a public key in PEM'},
        {'name':'ca_certs_path', 'help':"Path to a bundle of CA certificates in PEM"},
        {'name':'cert_path', 'help':"Path to a component's certificate in PEM"},
    ]
    
    def _update_crypto(self, args, copy_crypto_meth, update_secrets=False, conf_file_name=None,
            priv_key_name=None, pub_key_name=None, secret_names=[]):
        
        repo_dir = os.path.join(args.path, 'config', 'repo')
        secrets = {}
        
        if update_secrets:
            priv_key_location = os.path.abspath(os.path.join(repo_dir, priv_key_name))
            pub_key_location = os.path.abspath(os.path.join(repo_dir, pub_key_name))
            
            conf_location = os.path.join(repo_dir, conf_file_name)
            conf = anyjson.loads(open(conf_location).read())
            
            cm = CryptoManager(priv_key_location=priv_key_location)
            cm.load_keys()
            
            for name in secret_names:
                secrets[name] = cm.decrypt(conf[name])
            
        copy_crypto_meth(repo_dir, args)
        
        if update_secrets:
            cm.reset()
            cm.pub_key_location = pub_key_location
            cm.load_keys()
            
            for name in secret_names:
                conf[name] = cm.encrypt(secrets[name])
            
            open(conf_location, 'w').write(anyjson.dumps(conf))
    
    def _on_lb(self, args):
        self._update_crypto(args, self.copy_lb_crypto)
        
    def _on_zato_admin(self, args):
        self._update_crypto(args, self.copy_zato_admin_crypto, True, 'zato-admin.conf',
            'zato-admin-priv-key.pem', 'zato-admin-pub-key.pem', ['DATABASE_PASSWORD', 'TECH_ACCOUNT_PASSWORD'])

    #def _on_server(self, args):
    #    self._update_crypto(args, self.copy_zato_admin_crypto, True, 'zato-admin.conf',
    #        'zato-admin-priv-key.pem', 'zato-admin-pub-key.pem', ['DATABASE_PASSWORD', 'TECH_ACCOUNT_PASSWORD'])