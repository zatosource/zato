# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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

# Spring Python
from springpython.config import YamlConfig, XMLConfig
from springpython.context import ApplicationContext

# ConfigObj
from configobj import ConfigObj

# Zato
from zato.common.util import absolutize_path
from zato.server.config.app import ZatoContext

def _get_ioc_config(location, config_class):
    """ Instantiates an Inversion of Control container from the given location
    if the location exists at all.
    """
    stat = os.stat(location)
    if stat.st_size:
        config = config_class(location)
    else:
        config = None

    return config

def get_app_context(config):
    """ Returns the Zato's Inversion of Control application context, taking into
    account any custom user-provided contexts.
    """
    # Configure the IoC app context, including any customizations.
    app_ctx_list = [ZatoContext()]

    custom_ctx_section = config.get('custom_context', {})
    custom_xml_config_location = custom_ctx_section.get('custom_xml_config_location')
    custom_yaml_config_location = custom_ctx_section.get('custom_yaml_config_location')

    for location, config_class in ((custom_xml_config_location, XMLConfig), (custom_yaml_config_location, YamlConfig)):
        if location:
            ioc_config = _get_ioc_config(location, config_class)
            if ioc_config:
                app_ctx_list.append(ioc_config)

    return ApplicationContext(app_ctx_list)

def get_crypto_manager(repo_location, app_context, config, load_keys=True):
    """ Returns a tool for crypto manipulations.
    """
    crypto_manager = app_context.get_object('crypto_manager')
    
    priv_key_location = config['crypto']['priv_key_location']
    pub_key_location = config['crypto']['pub_key_location']
    cert_location = config['crypto']['cert_location']
    ca_certs_location = config['crypto']['ca_certs_location']
    
    priv_key_location = absolutize_path(repo_location, priv_key_location)
    pub_key_location = absolutize_path(repo_location, pub_key_location)
    cert_location = absolutize_path(repo_location, cert_location)
    ca_certs_location = absolutize_path(repo_location, ca_certs_location)
    
    crypto_manager.priv_key_location = priv_key_location
    crypto_manager.pub_key_location = pub_key_location
    crypto_manager.cert_location = cert_location
    crypto_manager.ca_certs_location = ca_certs_location
    
    if load_keys:
        crypto_manager.load_keys()
        
    return crypto_manager