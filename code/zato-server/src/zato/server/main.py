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

# Setting the customer logger must come first.
import logging
from zato.server.log import ZatoLogger
logging.setLoggerClass(ZatoLogger)

# stdlib
import os, sys
import logging.config

# ConfigObj
from configobj import ConfigObj

# Spring Python
from springpython.config import YamlConfig, XMLConfig
from springpython.context import ApplicationContext

# Zato
from zato.common.util import absolutize_path, TRACE1
from zato.server import get_config
from zato.server.config.app import ZatoContext

def _get_ioc_config(location, config_class):

    stat = os.stat(location)
    if stat.st_size:
        config = config_class(location)
    else:
        config = None

    return config

def run(host, port, base_dir, start_singleton):

    repo_location = os.path.join(base_dir, 'config', 'repo')

    # Configure the logging first, before configuring the actual server.
    logging.addLevelName('TRACE1', TRACE1)
    logging.config.fileConfig(os.path.join(repo_location, 'logging.conf'))

    config = get_config(repo_location)

    # Configure the IoC app context, including any customizations.
    app_ctx_list = [ZatoContext()]

    custom_ctx_section = config.get('custom_context', {})
    custom_xml_config_location = custom_ctx_section.get('custom_xml_config_location')
    custom_yaml_config_location = custom_ctx_section.get('custom_yaml_config_location')

    for location, config_class in ((custom_xml_config_location, XMLConfig),
                            (custom_yaml_config_location, YamlConfig)):

        if location:
            config = _get_ioc_config(location, config_class)
            if config:
                app_ctx_list.append(config)

    app_context = ApplicationContext(app_ctx_list)

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
    
    crypto_manager.load_keys()
    
    parallel_server = app_context.get_object('parallel_server')
    parallel_server.crypto_manager = crypto_manager
    parallel_server.odb.crypto_manager = crypto_manager
    parallel_server.odb.odb_data = config['odb']
    parallel_server.host = host
    parallel_server.port = port
    parallel_server.repo_location = repo_location
    
    if start_singleton:
        singleton_server = app_context.get_object('singleton_server')
        parallel_server.singleton_server = singleton_server
        
        # Wow, this line looks weird. What it does is simply assigning a parallel
        # server instance to the singleton server.
        parallel_server.singleton_server.parallel_server = parallel_server
        
    parallel_server.after_init()

    print('OK..')
    parallel_server.run_forever()
    
    # $ sudo netstat -an | grep TIME_WAIT | wc -l
    
    # cat /proc/sys/net/core/wmem_max - 109568
    # /sbin/sysctl net.ipv4.tcp_mem="109568 109568 109568"
    # echo 0 > /proc/sys/net/ipv4/conf/eth0/rp_filter


    '''
    job_list_location = os.path.join(repo_location, config['scheduler']['job_list_location'])
    service_store_config_location = os.path.join(repo_location, config['services']['service_store_config_location'])

    config_repo_manager = app_context.get_object('config_repo_manager')
    config_repo_manager.repo_location = repo_location
    config_repo_manager.job_list_location = job_list_location
    config_repo_manager.service_store_config_location = service_store_config_location

    scheduler = app_context.get_object('scheduler')
    scheduler.destroy_wait_time = int(config['scheduler']['destroy_wait_time'])
    scheduler.read_job_list(job_list_location)

    work_dir = config['pickup']['work_dir']
    if not os.path.isabs(work_dir):
        work_dir = os.path.join(repo_location, work_dir)

    egg_importer = app_context.get_object('egg_importer')
    egg_importer.work_dir = work_dir

    pickup_dir = config['pickup']['pickup_dir']
    if not os.path.isabs(pickup_dir):
        pickup_dir = os.path.join(repo_location, pickup_dir)

    pickup = app_context.get_object('pickup')
    pickup.pickup_dir = pickup_dir

    '''

if __name__ == '__main__':
    host, port, base_dir = sys.argv[1:4]
    start_singleton = True if len(sys.argv) >= 5 else False
    run(host, int(port), base_dir, start_singleton)