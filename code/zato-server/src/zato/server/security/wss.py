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
import logging, time
from hashlib import sha1
from string import Template
from datetime import datetime, timedelta

# lxml
from lxml import etree

# Spring Python
from springpython.context import ApplicationContextAware, ObjectPostProcessor

# Zato
from zato.common import soap_date_time_format
from zato.common import ZatoException, ClientSecurityException
from zato.common import(wss_namespaces, wsse_password_type_text, wsse_password_type_digest,
    wsse_username_path, wsse_username_xpath, wsse_password_path, wsse_password_xpath,
    wsse_password_type_path, wsse_password_type_xpath, wsse_nonce_path,
    wsse_nonce_xpath, wsu_username_created_path, wsu_username_created_xpath, wsse_username_objectify,
    wsse_username_token_objectify, supported_wsse_password_types, wsse_namespace,
    wsu_expires_path, wsu_expires_xpath)
from zato.common.util import TRACE1

wss_namespaces_log = "namespaces=[%s]" % wss_namespaces

error_msg_log = Template("$reason$expected_element $wss_namespaces $soap")
error_msg_response = Template("$reason$expected_element $wss_namespaces $soap")

class WSSUsernameTokenProfileStore(ApplicationContextAware):
    def __init__(self, config=None, definitions=None):
        self.config = config
        self.definitions = definitions
        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def needs_wss(self, service_class_name):
        result = service_class_name in self.config

        if self.logger.isEnabledFor(TRACE1):
            self.logger.log(TRACE1, "%s needs_wss -> [%s]" % (service_class_name, result))

        return result

    def _error(self, reason, soap, expected_element=""):

        # Note that we don't return the SOAP request in our own response.

        if expected_element:
            _expected_element = ". Expected element [%s]" % expected_element
            _wss_namespaces = wss_namespaces_log
        else:
            _expected_element = ""
            _wss_namespaces = ""

        msg_log = error_msg_log.safe_substitute(reason=reason,
            expected_element=_expected_element, wss_namespaces=_wss_namespaces,
            soap="soap=[%s]" % etree.tostring(soap))

        msg_response = error_msg_log.safe_substitute(reason=reason,
            expected_element=_expected_element, wss_namespaces=_wss_namespaces,
            soap="")

        self.logger.error(msg_log)
        raise ClientSecurityException(msg_response)

    def _replace_username_token_elem(self, soap, old_elem, attr_name):

        old_elem = old_elem[0]
        attr = old_elem.get(attr_name)
        username_token = soap.Header[wsse_username_objectify][wsse_username_token_objectify]

        elem_idx = username_token.index(old_elem)
        username_token.remove(old_elem)

        new_elem = etree.Element(old_elem.tag)
        new_elem.set(attr_name, attr)
        new_elem.text = "***"
        username_token.insert(elem_idx, new_elem)

        return old_elem.text, attr

    def _check_nonce(self, wsse_nonce, now, nonce_freshness_time):
        server = self.app_context.get_object("parallel_server")

        if wsse_nonce in server.wss_nonce_cache:
            return True

        # We don't have the nonce so let's tell the SingletonServer to add it
        # to caches of all parallel servers, including our own.

        recycle_time = (now + timedelta(seconds=nonce_freshness_time)).isoformat()
        server.send_config_request("ADD_TO_WSS_NONCE_CACHE", (wsse_nonce, recycle_time))

    def handle_request(self, service_class_name, service_data, soap):

        definition = self.definitions[self.config[service_class_name]]

        # Shadow the password and a nonce before any processing, getting
        # their values along the way.

        # TODO: Make shadowing a configurable option.

        wsse_password = wsse_password_xpath(soap)
        if wsse_password:
            wsse_password, wsse_password_type = self._replace_username_token_elem(soap, wsse_password, "Type")
        else:
            wsse_password_type = None

        wsse_nonce = wsse_nonce_xpath(soap)
        if wsse_nonce:
            wsse_nonce, wsse_encoding_type = self._replace_username_token_elem(soap, wsse_nonce, "EncodingType")
        else:
            wsse_encoding_type = None

        if self.logger.isEnabledFor(TRACE1):
            msg = "service_class_name=[%s], service_data=[%s], soap=[%s]"
            self.logger.log(TRACE1, msg % (service_class_name, service_data, etree.tostring(soap)))

        wsse_username = wsse_username_xpath(soap)
        if not wsse_username:
            self._error("No username sent", soap, wsse_username_path)

        wsse_username = wsse_username[0].text

        if wsse_username != definition["username"]:
            # To be on the safe side, we don't tell the requesting party what
            # exactly went wrong though we log details locally.

            msg = "Invalid username=[%s], soap=[%s]" % (wsse_username, etree.tostring(soap))
            self.logger.error(msg)

            raise ClientSecurityException("Invalid username or password")

        if not wsse_password_type:
            self._error("No password type sent", soap, wsse_password_type_path)

        if not wsse_password_type in supported_wsse_password_types:
            msg = "Unsupported password type=[%s], not in [%s]" % (wsse_password_type, supported_wsse_password_types)
            self._error(msg, soap)

        wsu_username_created = wsu_username_created_xpath(soap)
        if definition["reject_empty_nonce_creation_timestamp"] and not all((wsse_nonce, wsu_username_created)):
            self._error("Both nonce and creation timestamp must not be empty", soap)
        else:
            if wsu_username_created:
                wsu_username_created = wsu_username_created[0].text

        wsu_expires = wsu_expires_xpath(soap)
        if wsu_expires:
            wsu_expires = wsu_expires[0].text

        # Check nonce freshness and report an error if the UsernameToken is stale.
        now = datetime.utcnow()
        token_created = datetime.strptime(wsu_username_created, soap_date_time_format)

        elapsed = (now - token_created)

        if self.logger.isEnabledFor(logging.DEBUG):
            msg = "reject_stale_username_token=[%s], expiry_limit=[%s], now=[%r], token_created=[%r], elapsed=[%r]"
            self.logger.debug(msg % (definition["reject_stale_username_token"],
                                     definition["expiry_limit"], now, token_created, elapsed))

        if definition["reject_stale_username_token"] and elapsed.seconds > definition["expiry_limit"]:
            msg = "UsernameToken has expired, reject_stale_username_token=[%s], "\
                "expiry_limit=[%s], wsu_username_created=[%s], elapsed=[%s]"
            self.logger.error(msg % (definition["reject_stale_username_token"],
                                     definition["expiry_limit"], wsu_username_created, elapsed))
            raise ClientSecurityException("UsernameToken has expired")

        # Let's see if the nonce is correct.
        nonce = wsse_nonce.decode("base64")
        concat = nonce + wsu_username_created + definition["password"]

        h = sha1()
        h.update(concat)

        digest = str.encode(h.digest(), "base64").rstrip("\n")

        if wsse_password != digest:
            # Same as above, we don't want to reveal to much details to the
            # other side.

            msg = "Invalid wsse_password=[%s], wsse_username=[%s], soap=[%s]" % (
                wsse_password, wsse_username, etree.tostring(soap))
            self.logger.error(msg)

            raise ClientSecurityException("Invalid username or password")

        # Have we already seen such a nonce?
        if self._check_nonce(wsse_nonce, now, definition["nonce_freshness_time"]):
            raise ClientSecurityException("Nonce is not unique")
