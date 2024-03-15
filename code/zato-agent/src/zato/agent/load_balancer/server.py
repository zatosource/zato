# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import logging.config
import os
import ssl
from collections import Counter
from datetime import datetime
from http.client import OK
from traceback import format_exc
from typing import Callable

# pytz
from pytz import utc

# YAML
import yaml

# Python 2/3 compatibility
from zato.common.ext.future.moves.urllib.request import urlopen
from six import PY2

# Zato
from zato.agent.load_balancer.config import backend_template, config_from_string, string_from_config, zato_item_token
from zato.agent.load_balancer.haproxy_stats import HAProxyStats
from zato.common.api import HAProxy,  MISC, TRACE1, ZATO_OK
from zato.common.haproxy import haproxy_stats, validate_haproxy_config
from zato.common.py23_.spring_ import RequestHandler, SimpleXMLRPCServer, SSLServer
from zato.common.repo import RepoManager
from zato.common.util.api import get_lb_agent_json_config, timeouting_popen
from zato.common.util.open_ import open_r, open_w
from zato.common.util.platform_ import is_linux

public_method_prefix = '_lb_agent_'
config_file = 'zato.config'

logger = logging.getLogger('')
logging.addLevelName(TRACE1, 'TRACE1')

# All known HAProxy commands
haproxy_commands = {}
for _ignored_version, commands in haproxy_stats.items():
    haproxy_commands.update(commands)

# ################################################################################################################################
# ################################################################################################################################

class BaseLoadBalancerAgent:

    # This is implemented by children classes
    register_function: Callable

    def init_config(self, repo_dir):

        self.repo_dir = os.path.abspath(repo_dir)
        self.json_config = get_lb_agent_json_config(self.repo_dir)

        self.work_dir = os.path.abspath(os.path.join(self.repo_dir, self.json_config['work_dir']))
        self.haproxy_command = self.json_config['haproxy_command']
        self.verify_fields = self.json_config['verify_fields']

        self.keyfile = os.path.abspath(os.path.join(self.repo_dir, self.json_config['keyfile']))
        self.certfile = os.path.abspath(os.path.join(self.repo_dir, self.json_config['certfile']))
        self.ca_certs = os.path.abspath(os.path.join(self.repo_dir, self.json_config['ca_certs']))

        self.haproxy_pidfile = os.path.abspath(os.path.join(self.repo_dir, '../', '../', MISC.PIDFILE))

        log_config = os.path.abspath(os.path.join(self.repo_dir, self.json_config['log_config']))
        with open_r(log_config) as f:
            data = yaml.load(f, yaml.FullLoader) # type: dict
            logging.config.dictConfig(data) # pyright: reportGeneralTypeIssues=false

        self.config_path = os.path.join(self.repo_dir, config_file)
        self.config = self._read_config()
        self.start_time = datetime.utcnow().replace(tzinfo=utc).isoformat()
        self.haproxy_stats = HAProxyStats(self.config.global_['stats_socket'])

        RepoManager(self.repo_dir).ensure_repo_consistency()

        self.host = self.json_config['host']
        self.port = self.json_config['port']

        self.logger = logging.getLogger(self.__class__.__name__)

# ################################################################################################################################

    def _re_start_load_balancer(self, timeout_msg, rc_non_zero_msg, additional_params=None):
        """ A common method for (re-)starting HAProxy.
        """
        additional_params = additional_params or []
        command = [self.haproxy_command, '-D']
        if is_linux:
            command.extend(['-m', HAProxy.Default_Memory_Limit])
        command.extend(['-f', self.config_path, '-p', self.haproxy_pidfile])
        command.extend(additional_params)
        timeouting_popen(command, 5.0, timeout_msg, rc_non_zero_msg)

# ################################################################################################################################

    def start_load_balancer(self):
        """ Starts the HAProxy load balancer in background.
        """
        self._re_start_load_balancer("HAProxy didn't start in `{}` seconds. ", 'Failed to start HAProxy. ')

# ################################################################################################################################

    def restart_load_balancer(self):
        """ Restarts the HAProxy load balancer without disrupting existing connections.
        """
        additional_params = [
            '-sf',
            open_r(self.haproxy_pidfile).read().strip()
        ]
        self._re_start_load_balancer('Could not restart in `{}` seconds. ', 'Failed to restart HAProxy. ', additional_params)

# ################################################################################################################################

    def register_functions(self):
        """ All methods with the '_lb_agent_' prefix will be exposed through
        SSL XML-RPC after chopping off the prefix, so that self._lb_agent_ping
        becomes a 'ping' method, self._lb_agent_get_uptime_info -> 'get_uptime_info'
        etc.
        """
        for item in sorted(dir(self)):
            if item.startswith(public_method_prefix):
                public_name = item.split(public_method_prefix)[1]
                attr = getattr(self, item)
                msg = 'Registering `{attr}` under public name `{public_name}`'
                logger.info(msg.format(attr=attr, public_name=public_name))
                self.register_function(attr, public_name)

# ################################################################################################################################

    def _read_config_string(self):
        """ Returns the HAProxy config as a string.
        """
        return open_r(self.config_path).read()

# ################################################################################################################################

    def _read_config(self):
        """ Read and parse the HAProxy configuration.
        """
        return config_from_string(self._read_config_string())

# ################################################################################################################################

    def _validate(self, config_string):
        validate_haproxy_config(config_string, self.haproxy_command)

# ################################################################################################################################

    def _save_config(self, config_string):
        """ Save a new HAProxy config file on disk. It is assumed the file
        has already been validated.
        """
        f = open_w(self.config_path)
        f.write(config_string)
        f.close()

        self.config = self._read_config()

# ################################################################################################################################

    def _validate_save_config_string(self, config_string, save):
        """ Given a string representing the HAProxy config file it first validates
        it and then optionally saves it and restarts the load balancer.
        """
        self._validate(config_string)

        if save:
            self._save_config(config_string)
            self.restart_load_balancer()

        return True

# ################################################################################################################################

    def _show_stat(self):
        stat = self.haproxy_stats.execute('show stat')

        for line in stat.splitlines():
            if line.startswith('#') or not line.strip():
                continue
            line = line.split(',')

            haproxy_name = line[0]
            haproxy_type_or_name = line[1]

            if haproxy_name.startswith('bck') and not haproxy_type_or_name == 'BACKEND':
                backend_name, state = line[1], line[17]

                # Do not count in backends other than Zato, e.g. perhaps someone added their own
                if not 'http_plain' in backend_name:
                    continue

                access_type, server_name = backend_name.split('--')

                yield access_type, server_name, state

# ################################################################################################################################

    def _lb_agent_validate_save_source_code(self, source_code, save=False):
        """ Validate or validates & saves (if 'save' flag is True) an HAProxy
        configuration passed in as a string. Note that the validation step is always performed.
        """
        return self._validate_save_config_string(source_code, save)

# ################################################################################################################################

    def _lb_agent_validate_save(self, lb_config, save=False):
        """ Validate or validates /and/ saves (if 'save' flag is True) an HAProxy
        configuration. Note that the validation step is always performed.
        """
        config_string = string_from_config(lb_config, open_r(self.config_path).readlines())
        return self._validate_save_config_string(config_string, save)

# ################################################################################################################################

    def _lb_agent_get_servers_state(self):
        """ Return a three-key dictionary describing the current state of all Zato servers
        as seen by HAProxy. Keys are "UP" for running servers, "DOWN" for those
        that are unavailable, and "MAINT" for servers in the maintenance mode.
        Values are dictionaries of access type -> names of servers. For instance,
        if there are three servers, one is UP, the second one is DOWN and the
        third one is MAINT, the result will be:

        {
          'UP': {'http_plain': ['SERVER.1']},
          'DOWN': {'http_plain': ['SERVER.2']},
          'MAINT': {'http_plain': ['SERVER.3']},
        }
        """
        servers_state = {
            'UP': {'http_plain':[]},
            'DOWN': {'http_plain':[]},
            'MAINT': {'http_plain':[]},
        }

        for access_type, server_name, state in self._show_stat():
            # Don't bail out when future HAProxy versions introduce states
            # we aren't currently aware of.
            if state not in servers_state:
                msg = 'Encountered unknown state [{state}], recognized ones are [{states}]'
                logger.warning(msg.format(state=state, states=str(sorted(servers_state))))
            else:
                servers_state[state][access_type].append(server_name)
        return servers_state

# ################################################################################################################################

    def _lb_agent_get_server_data_dict(self, name=None):
        """ Returns a dictionary whose keys are server names and values are their
        access types and the server's status as reported by HAProxy.
        """
        backend_config = self.config.backend['bck_http_plain']
        servers = {}

        def _dict(access_type, state, server_name):
            return {
                'access_type':access_type,
                'state':state,
                'address': '{}:{}'.format(backend_config[server_name]['address'], backend_config[server_name]['port'])
            }

        for access_type, server_name, state in self._show_stat():
            if name:
                if name == server_name:
                    servers[server_name] = _dict(access_type, state, server_name)
            else:
                servers[server_name] = _dict(access_type, state, server_name)

        return servers

# ################################################################################################################################

    def _lb_agent_rename_server(self, old_name, new_name):
        """ Renames the server, validates and saves the config.
        """
        if old_name == new_name:
            msg = 'Skipped renaming, old_name:[{}] is the same as new_name:[{}]'.format(old_name, new_name)
            self.logger.warning(msg)
            return True

        new_config = []
        config_string = self._read_config_string()
        old_servers = Counter()
        new_servers = Counter()

        def _get_lines():
            for line in config_string.splitlines():
                yield line

        old_server = '# ZATO backend bck_http_plain:server--{}'.format(old_name)
        new_server = '# ZATO backend bck_http_plain:server--{}'.format(new_name)

        for line in _get_lines():
            if old_server in line:
                old_servers[old_name] += 1

            if new_server in line:
                new_servers[new_name] += 1

        if not old_servers[old_name]:
            raise Exception("old_name:[{}] not found in the load balancer's configuration".format(old_name))

        if new_servers[new_name]:
            raise Exception('new_name:[{}] is not unique'.format(new_name))

        for line in _get_lines():
            if old_server in line:
                line = line.replace(old_name, new_name)
            new_config.append(line)

        self._validate_save_config_string('\n'.join(new_config), True)

        return True

# ################################################################################################################################

    def _lb_agent_add_remove_server(self, action, server_name):
        bck_http_plain = self.config.backend['bck_http_plain']

        if action == 'remove':
            del bck_http_plain[server_name]
        elif action == 'add':
            bck_http_plain[server_name] = {}
            bck_http_plain[server_name]['extra'] = 'check inter 2s rise 2 fall 2'
            bck_http_plain[server_name]['address'] = '127.0.0.1'
            bck_http_plain[server_name]['port'] = '123456'
        else:
            raise Exception('Unrecognized action:[{}]'.format(action))

        new_config = []
        config_string = self._read_config_string()

        for line in config_string.splitlines():
            if '# ZATO backend bck_http_plain' in line:
                continue
            else:
                backends = []
                if '# ZATO begin backend bck_http_plain' in line:
                    for server_name in bck_http_plain:
                        data_dict = {
                            'server_type':'http_plain',
                            'server_name':server_name,
                            'address':bck_http_plain[server_name]['address'],
                            'port':bck_http_plain[server_name]['port'],
                            'extra':bck_http_plain[server_name]['extra'],
                            'zato_item_token':zato_item_token,
                            'backend_type':'bck_http_plain',

                        }
                        backends.append(backend_template.format(**data_dict))
                line += ('\n' * 2) + '\n'.join(backends)
            new_config.append(line.rstrip())

        self._validate_save_config_string('\n'.join(new_config), True)

        return True

# ################################################################################################################################

    def _lb_agent_execute_command(self, command, timeout, extra=''):
        """ Execute an HAProxy command through its UNIX socket interface.
        """
        command = haproxy_commands[int(command)][0]
        timeout = int(timeout)

        result = self.haproxy_stats.execute(command, extra, timeout)

        # Special-case the request for describing the commands available.
        # There's no 'describe commands' command in HAProxy but HAProxy is
        # nice enough to return a usage info when it encounters an unknown
        # command which we parse and return to the caller.
        if command == 'ZATO_DESCRIBE_COMMANDS':
            result = '\n\n' + '\n'.join(result.splitlines()[1:])

        return result

# ################################################################################################################################

    def _lb_agent_haproxy_version_info(self):
        """ Return a three-element tuple describing HAProxy's version,
        similar to what stdlib's sys.version_info does.
        """
        # 'show info' is always available and we use it for determining the HAProxy version.
        info = self.haproxy_stats.execute('show info')
        for line in info.splitlines():
            if line.startswith('Version:'):
                version = line.split('Version:')[1]
                return version.strip().split('.')

# ################################################################################################################################

    def _lb_agent_ping(self):
        """ Always return ZATO_OK.
        """
        return ZATO_OK

# ################################################################################################################################

    def _lb_agent_get_config(self):
        """ Return those pieces of an HAProxy configuration that are understood
        by Zato.
        """
        return self.config

# ################################################################################################################################

    def _lb_agent_get_config_source_code(self):
        """ Return the HAProxy configuration file's source.
        """
        return self._read_config_string()

# ################################################################################################################################

    def _lb_agent_get_uptime_info(self):
        """ Return the agent's (not HAProxy's) uptime info, currently returns
        only the time it was started at.
        """
        return self.start_time

# ################################################################################################################################

    def _lb_agent_is_haproxy_alive(self, lb_use_tls):
        """ Invoke HAProxy through HTTP monitor_uri and return ZATO_OK if
        HTTP status code is 200. Raise Exception otherwise.
        """
        host = self.config.frontend['front_http_plain']['bind']['address']
        port = self.config.frontend['front_http_plain']['bind']['port']
        path = self.config.frontend['front_http_plain']['monitor_uri']

        url = 'http{}://{}:{}{}'.format('s' if lb_use_tls else '', host, port, path)

        try:
            conn = urlopen(url)
        except Exception:
            msg = 'Could not open URL `{}`, e:`{}`'.format(url, format_exc())
            logger.error(msg)
            raise Exception(msg)
        else:
            try:
                code = conn.getcode()
                if code == OK:
                    return ZATO_OK
                else:
                    msg = 'Could not open URL [{url}], HTTP code:[{code}]'.format(url=url, code=code)
                    logger.error(msg)
                    raise Exception(msg)
            finally:
                conn.close()

# ################################################################################################################################

    def _lb_agent_get_work_config(self):
        """ Return the agent's basic configuration.
        """
        return {'work_dir':self.work_dir, 'haproxy_command':self.haproxy_command, # noqa
                'keyfile':self.keyfile, 'certfile':self.certfile,                 # noqa
               'ca_certs':self.ca_certs, 'verify_fields':self.verify_fields}      # noqa

# ################################################################################################################################
# ################################################################################################################################

class LoadBalancerAgent(BaseLoadBalancerAgent, SimpleXMLRPCServer):
    def __init__(self, repo_dir):
        self.init_config(repo_dir)

        if PY2:
            SimpleXMLRPCServer.__init__(self, (self.host, self.port), requestHandler=RequestHandler)
        else:
            SimpleXMLRPCServer.__init__(self, (self.host, self.port))

        self.register_functions()

# ################################################################################################################################
# ################################################################################################################################

class TLSLoadBalancerAgent(BaseLoadBalancerAgent, SSLServer):
    def __init__(self, repo_dir):
        self.init_config(repo_dir)

        SSLServer.__init__(self, host=self.host, port=self.port, keyfile=self.keyfile, certfile=self.certfile,
            ca_certs=self.ca_certs, cert_reqs=ssl.CERT_REQUIRED, verify_fields=self.verify_fields)

        self.register_functions()

# ################################################################################################################################
# ################################################################################################################################
