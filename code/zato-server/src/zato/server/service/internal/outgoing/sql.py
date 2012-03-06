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


'''
from __future__ import absolute_import, division, print_function, unicode_literals

# lxml
from lxml import etree

# Spring Python
from springpython.util import synchronized

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.util import pprint, TRACE1
from zato.server.service.internal import _get_params, _parse_extra_params, AdminService

class GetSQLConnectionPoolList(AdminService):
    """ Returns a list of all SQL connection pools defined.
    """
    def handle(self, *args, **kwargs):

        # Parallel servers are always are up to date with information about
        # SQL pools, no need to ask the singleton server.

        pool_list = etree.Element("pool_list")

        def _create_elem(pool_name, elem_name):
            elem_info = self.server.sql_pool.pool_list[pool_name].get(elem_name, {})

            if elem_name == "extra":
                extra_list = etree.Element(elem_name)
                for extra_param_name in elem_info:
                    extra_elem = etree.Element("item")
                    extra_elem.text = "%s=%s" % (extra_param_name, elem_info[extra_param_name])
                    extra_list.append(extra_elem)

                return extra_list
            else:

                if elem_name == "pool_size":
                    elem_info = str(elem_info)

                elem = etree.Element(elem_name)
                elem.text = elem_info if elem_info else ""

                return elem

        for pool_name in sorted(self.server.sql_pool.pool_list):
            pool = etree.Element("pool")
            name = etree.Element("pool_name")
            name.text = pool_name
            pool.append(name)
            pool_list.append(pool)

            pool.append(_create_elem(pool_name, "engine"))
            pool.append(_create_elem(pool_name, "user"))
            pool.append(_create_elem(pool_name, "host"))
            pool.append(_create_elem(pool_name, "db_name"))
            pool.append(_create_elem(pool_name, "pool_size"))
            pool.append(_create_elem(pool_name, "extra"))

        return ZATO_OK, etree.tostring(pool_list)

class CreateSQLConnectionPool(AdminService):
    """ Creates a new SQL connection pool.
    """
    @synchronized()
    def handle(self, *args, **kwargs):

        payload = kwargs.get("payload")
        request_params = ["pool_name", "engine", "user", "host", "db_name", "pool_size"]
        new_params = _get_params(payload, request_params, "pool.")
        new_params["extra"] = _parse_extra_params(payload)

        new_params_pprinted = pprint(new_params)

        self.logger.debug("Will create an SQL connection pool, new_params=[%s]" % new_params_pprinted)

        result, response = self.server.send_config_request("CREATE_SQL_CONNECTION_POOL",
                        new_params, timeout=6.0)
        self.logger.log(TRACE1, "result=[%s], response=[%s]" % (result, response))

        return result, response

class EditSQLConnectionPool(AdminService):
    """ Updates all of SQL connection pool's parameters, except for the password.
    """
    @synchronized()
    def handle(self, *args, **kwargs):

        payload = kwargs.get("payload")
        request_params = ["original_pool_name", "pool_name", "engine", "user", "host", "db_name", "pool_size"]
        new_params = _get_params(payload, request_params, "pool.")
        new_params["extra"] = _parse_extra_params(payload)

        new_params_pprinted = pprint(new_params)

        self.logger.debug("About to update an SQL connection pool, new_params=[%s]" % new_params_pprinted)

        result, response = self.server.send_config_request("EDIT_SQL_CONNECTION_POOL",
                        new_params, timeout=6.0)
        self.logger.log(TRACE1, "result=[%s], response=[%s]" % (result, response))

        return result, response

class ChangePasswordSQLConnectionPool(AdminService):
    """ Changes the SQL connection pool's password.
    """
    @synchronized()
    def handle(self, *args, **kwargs):

        payload = kwargs.get("payload")
        request_params = ["pool_name", "password1", "password2"]
        new_params = _get_params(payload, request_params)

        password1 = self.server.crypto_manager.decrypt(new_params["password1"])
        password2 = self.server.crypto_manager.decrypt(new_params["password2"])

        if password1 != password2:
            raise ZatoException("Passwords do not match.")

        params = {"pool_name": new_params["pool_name"],
            "password":password1,
            "password_encrypted": new_params["password1"]
        }

        result, response = self.server.send_config_request("CHANGE_PASSWORD_SQL_CONNECTION_POOL",
                        params, timeout=6.0)
        self.logger.log(TRACE1, "result=[%s], response=[%s]" % (result, response))

        return result, response

class PingSQLConnectionPool(AdminService):
    """ Pings the connection pool and returns a response time. Since ParallelServers
    are always up to date with information regarding SQL connection pools, we can
    ping the database directly here.
    """
    def handle(self, *args, **kwargs):
        payload = kwargs.get("payload")
        request_params = ["pool_name"]
        new_params = _get_params(payload, request_params)

        response_time = self.server.sql_pool.ping(new_params)
        response_time_elem = etree.Element("response_time")
        response_time_elem.text = str(response_time)

        return ZATO_OK, etree.tostring(response_time_elem)

class DeleteSQLConnectionPool(AdminService):
    """ Deletes the SQL connection pool.
    """
    def handle(self, *args, **kwargs):
        payload = kwargs.get("payload")
        request_params = ["pool_name"]
        new_params = _get_params(payload, request_params)

        result, response = self.server.send_config_request("DELETE_SQL_CONNECTION_POOL",
                        new_params, timeout=6.0)
        self.logger.log(TRACE1, "result=[%s], response=[%s]" % (result, response))

        return result, response
'''
