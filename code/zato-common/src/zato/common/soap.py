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
import logging
from string import Template
from traceback import format_exc

# lxml
from lxml import etree
from lxml import objectify

# urllib3
import urllib3

# Zato
from zato.common.util import TRACE1
from zato.common import soap_doc, soap_fault_xpath, ZATO_ERROR, ZATO_OK
from zato.common import ZatoException, zato_data_xpath, zato_error_code_path_xpath

logger = logging.getLogger(__name__)

class SOAPPool(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self._pool = urllib3.connection_from_url(self.url, **kwargs)

    def __str__(self):
        return '<{0} object at {1}, url=[{2}]>'.format(self.__class__.__name__, hex(id(self)), self.url)

    def invoke(self, script_path, soap_action, soap_body, headers={}):
        msg_headers = {'content-type': 'text/xml', 'SOAPAction': soap_action}
        msg_headers.update(**headers)
        payload = soap_doc.safe_substitute(body=soap_body)

        msg = 'About to invoke a service. url=[{0}] script_path=[{1}] msg_headers=[{2}] soap_body=[{3}]'.format(
            self.url, script_path, msg_headers, soap_body)
        logger.debug(msg)
        

        response = self._pool.urlopen('POST', script_path, payload, msg_headers).data
        logger.debug('Received a response [{0}]'.format(response))

        return response

def invoke_admin_service(cluster, soap_action, soap_body="", headers={}, needs_config_key=False):
    """ Invokes a Zato server's administrative SOAP service. Returns an lxml's objectified
    response if no errors have been encountered. Raises a ZatoException if the response
    doesn't pass the formal validation.

    cluster - a cluster whose load balancer will be invoked
    soap_action - a SOAP action to invoke
    soap_body - an optional SOAP payload to pass to the admin service
    needs_config_key - whether the invoker should validate that a server's config crypto key
                       has been returned in the response. Will raise a ZatoException if it hasn't
                       and 'needs_config_key' is True.
    """
    url = 'https://{0}:{1}'.format(cluster.sec_server_host, cluster.sec_server_port)
    logger.log(TRACE1, 'About to invoke admin service url=[{0}]'.format(url))
    pool = SOAPPool(url)
    soap_response = pool.invoke('/zato/soap', soap_action, soap_body, headers)


    print('soap_response=[{0}]'.format(soap_response))
    response = objectify.fromstring(soap_response)

    # Do we have a SOAP fault?
    if soap_fault_xpath(response):
        msg = "Server returned a SOAP fault, soap_response=[%s]" % soap_response
        logger.error(msg)
        raise ZatoException(msg)

    # Did server send a business payload, i.e. a <data> elem in the Zato's namespace?
    zato_data = zato_data_xpath(response)
    if not zato_data:
        msg = "Server did not send a business payload (zato_message.data element is missing), soap_response=[%s]" % soap_response
        logger.error(msg)
        raise ZatoException(msg)

    zato_message = zato_data[0].getparent()
    logger.log(TRACE1, "zato_message=[%s]" % etree.tostring(zato_message))

    # We have a payload but hadn't there been any errors at the server's side?
    zato_error_code = zato_error_code_path_xpath(response)
    if zato_error_code[0] != ZATO_OK:
        logger.log(TRACE1, "zato_error_code=[%s]" % zato_error_code)
        raise ZatoException(soap_response)

    # Check whether the key has been received, if one has been requested.
    if needs_config_key:
        try:
            zato_message.envelope.config_pub_key
        except AttributeError, e:
            logger.error(e)
            msg = "A server's config crypto key has been requested but none has " \
                  "been received from the server, soap_response=[%s], traceback=[%s]" % (soap_response, format_exc())
            logger.error(msg)
            raise ZatoException(msg)

    return ZATO_OK, zato_message, soap_response
