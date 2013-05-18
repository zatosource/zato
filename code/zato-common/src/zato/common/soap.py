# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# lxml
from lxml import etree
from lxml import objectify

# urllib3
import urllib3

# Zato
from zato.common.util import TRACE1
from zato.common import soap_doc, soap_fault_xpath, ZATO_OK
from zato.common import ZatoException, zato_data_path, zato_data_xpath, zato_result_xpath

logger = logging.getLogger(__name__)

class SOAPPool(object):
    def __init__(self, url, **kwargs):
        self.url = url
        self._pool = urllib3.connection_from_url(self.url, **kwargs)

    def __str__(self):
        return '<{0} object at {1}, url:[{2}]>'.format(self.__class__.__name__, hex(id(self)), self.url)

    def invoke(self, script_path, soap_action, soap_body, headers={}):
        msg_headers = {'content-type': 'text/xml', 'SOAPAction': soap_action}
        msg_headers.update(**headers)
        payload = soap_doc.safe_substitute(body=soap_body)

        msg = 'About to invoke a service. url:[{0}] script_path:[{1}] msg_headers:[{2}] soap_body:[{3}]'.format(
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
    url = ''
    path = ''
    soap_response = ''
    try:
        url = 'http://{0}:{1}'.format(cluster.lb_host, cluster.lb_port)
        path = '/zato/soap'
        logger.log(TRACE1, 'About to invoke the admin service url:[{0}]'.format(url))
        pool = SOAPPool(url)
        soap_response = pool.invoke(path, soap_action, soap_body, headers)
        
        try:
            logger.log(TRACE1, 'soap_response:[{0}]'.format(soap_response))
            response = objectify.fromstring(soap_response)
        except Exception, e:
            msg = 'Could not parse the SOAP response:[{}]'.format(soap_response)
            raise Exception(msg)
    
        # Do we have a SOAP fault?
        if soap_fault_xpath(response):
            msg = "Server returned a SOAP fault, soap_response:[%s]" % soap_response
            logger.error(msg)
            raise ZatoException(msg=msg)
    
        # Did server send a business payload, i.e. a <data> elem in the Zato's namespace?
        zato_data = zato_data_xpath(response)
        if not zato_data:
            msg = 'Server did not send a business payload ({} element is missing), soap_response:[{}]'.format(zato_data_path, soap_response)
            logger.error(msg)
            raise ZatoException(msg=msg)
    
        zato_message = zato_data[0]
        logger.log(TRACE1, "zato_message:[%s]" % etree.tostring(zato_message))
    
        # We have a payload but hadn't there been any errors at the server's side?
        zato_result = zato_result_path_xpath(response)
        if zato_result[0] != ZATO_OK:
            logger.log(TRACE1, "zato_result:[%s]" % zato_result)
            raise ZatoException(msg=soap_response)
    
        # Check whether the key has been received, if one has been requested.
        if needs_config_key:
            try:
                zato_message.envelope.config_pub_key
            except AttributeError, e:
                logger.error(e)
                msg = "A server's config crypto key has been requested but none has " \
                      "been received from the server, soap_response:[%s], traceback:[%s]" % (soap_response, format_exc())
                logger.error(msg)
                raise ZatoException(msg=msg)
    
        return zato_message, soap_response
    except Exception, e:
        log_msg = 'Could not invoke the service. url:[{}] path:[{}] soap_action:[{}] '\
                  'soap_body:[{}] headers:[{}] soap_response:[{}], e:[{}]'.format(
                      url, path, soap_action, soap_body, headers, soap_response, format_exc(e))
        logger.error(log_msg)
        raise
