# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Dashboard entry points of the services under test - the IDE, the Invoke overlays of the REST, SOAP and MLLP
# channels and the Publish overlay of a topic - and the deployment of the services with their definitions.

# stdlib
import time

# Zato
from zato.common.test.playwright_pubsub import get_item_id as get_topic_id, navigate_to_page, open_publish_overlay, \
    publish_via_overlay
from zato.common.test.service_entry_points.models import ServiceName

# Playwright helpers
from mcp_gateway_live import import_enmasse
from mllp_channel import Channel_Page_Url as MLLP_Channel_Page_Url, get_item_id as get_mllp_channel_id
from rest_channel import deploy_service_file, get_channel_id, open_channel_page, wait_for_channel_row
from soap_channel import open_soap_channel_page

# Service entry points
from service_entry_points.compare import take_reference
from service_entry_points.requests import All_Targets, Module, read_source, render_definitions, Source

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from service_entry_points.compare import references_dict
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class PayloadFormat:
    """ The formats of the IDE that the services under test take their requests in.
    """
    JSON = 'json'
    HL7  = 'hl7-v2'

# ################################################################################################################################

class Timeout:
    """ How long each step waits, in seconds for the deployment and in milliseconds for the pages.
    """
    Deployment     = 120
    Page_Ready     = 15_000
    Invocation     = 60_000
    Overlay_Opened = 5_000

# ################################################################################################################################

# The pages of Dashboard that the entry points are on
_ide_page_url = '/zato/service/ide/service/{}/'
_topic_page_url = '/zato/pubsub/topic/'

# How long to wait between checks of the deployment, in seconds
_deployment_poll_interval = 1

# Whether the status line of an overlay shows the outcome of an invocation
_is_overlay_done = '''() => {
    let status = document.querySelector("#invoker-modal-status");
    let text = status.textContent;
    return text.indexOf("Invoking") === -1 && text.trim().length > 0;
}'''

# Whether the response pane of the IDE shows the response of an invocation
_is_ide_done = 'document.querySelector("#data-response").value.length > 0'

# ################################################################################################################################
# ################################################################################################################################

def _is_deployed(api_client:'any_') -> 'bool':
    """ Whether the server has the services under test deployed, the module being deployed as one.
    """
    try:
        _ = api_client.invoke(ServiceName.Read)

    # The server refuses the request for a service that it does not have
    except Exception:
        return False

    return True

# ################################################################################################################################

def deploy(zato_dashboard:'anydict', api_client:'any_', caller_password:'str') -> 'str':
    """ Deploys the services under test through the pickup directory, waits for them, imports their channels,
    topics and subscriptions, and returns the path of the deployed module.
    """
    source = read_source(Source.Services)
    out = deploy_service_file(zato_dashboard['server_dir'], Module.File_Name, source)

    deadline = time.monotonic() + Timeout.Deployment

    while not _is_deployed(api_client):
        if time.monotonic() >= deadline:
            raise Exception(f'Service {ServiceName.Read} was not deployed within {Timeout.Deployment}s')
        time.sleep(_deployment_poll_interval)

    import_enmasse(zato_dashboard, render_definitions(caller_password))

    return out

# ################################################################################################################################

def take_references(api_client:'any_') -> 'references_dict':
    """ The record and the response of each service under test invoked through self.invoke, keyed by its kind.
    """
    out:'references_dict' = {}

    for target in All_Targets:
        out[target.kind] = take_reference(api_client, target)

    return out

# ################################################################################################################################
# ################################################################################################################################

def invoke_in_ide(page:'Page', base_url:'str', service_name:'str', payload_format:'str', request_text:'str') -> 'str':
    """ Invokes a service from its page in the IDE with the request in the given format and returns the text
    of the response pane.
    """
    _ = page.goto(base_url + _ide_page_url.format(service_name))
    _ = page.wait_for_selector('#invoke-service:not([disabled])', state='visible', timeout=Timeout.Page_Ready)

    # The format is chosen the way a person chooses it, which also sets the format the request travels in ..
    _ = page.select_option('#payload-format-select', payload_format)

    # .. the previous response is cleared so that the new one can be told apart ..
    page.evaluate('$("#data-response").val("")')
    page.fill('#data-request', request_text)

    def _is_invoke_response(response:'any_') -> 'bool':
        out = '/zato/service/invoke/' in response.url
        return out

    # .. and the response pane is read once the invocation completes.
    with page.expect_response(_is_invoke_response, timeout=Timeout.Invocation):
        page.click('#invoke-service')

    _ = page.wait_for_function(_is_ide_done, timeout=Timeout.Invocation)

    out = page.input_value('#data-response')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _invoke_in_overlay(page:'Page', request_text:'str') -> 'str':
    """ Enters a request into the open Invoke overlay, invokes it and returns the raw response, closing the overlay.
    """
    page.evaluate('text => $.fn.zato.invoker._request_pane.setValue(text)', request_text)
    page.evaluate('$("#invoker-modal-status").text("")')

    page.click('#invoker-modal-invoke-button')
    _ = page.wait_for_function(_is_overlay_done, timeout=Timeout.Invocation)

    out = page.evaluate('$("#invoker-modal-response-pane").data("raw-response")')
    page.evaluate('$.fn.zato.invoker.close_overlay()')

    return out

# ################################################################################################################################

def _wait_for_overlay(page:'Page') -> 'None':
    _ = page.wait_for_selector('#invoker-modal-overlay:not(.hidden)', state='visible', timeout=Timeout.Overlay_Opened)

# ################################################################################################################################

def invoke_rest_channel(page:'Page', base_url:'str', channel_name:'str', request_text:'str') -> 'str':
    """ Invokes a REST channel from the Invoke link of its row and returns the raw response.
    """
    open_channel_page(page, base_url, channel_name)
    _ = wait_for_channel_row(page, channel_name)

    channel_id = get_channel_id(page, channel_name)
    page.evaluate('channelId => $.fn.zato.http_soap.invoke(channelId)', channel_id)
    _wait_for_overlay(page)

    out = _invoke_in_overlay(page, request_text)
    return out

# ################################################################################################################################

def invoke_soap_channel(page:'Page', base_url:'str', channel_name:'str', envelope:'str') -> 'str':
    """ Invokes a SOAP channel with an envelope from the Invoke link of its row and returns the raw response.
    """
    open_soap_channel_page(page, base_url, channel_name)
    _ = wait_for_channel_row(page, channel_name)

    channel_id = get_channel_id(page, channel_name)
    page.evaluate('channelId => $.fn.zato.http_soap.invoke(channelId)', channel_id)
    _wait_for_overlay(page)

    out = _invoke_in_overlay(page, envelope)
    return out

# ################################################################################################################################

def invoke_mllp_channel(page:'Page', base_url:'str', channel_name:'str', message:'str') -> 'str':
    """ Sends an HL7 v2 message to an MLLP channel from the Invoke link of its row and returns the acknowledgment.
    """
    navigate_to_page(page, base_url, f'{MLLP_Channel_Page_Url}&query={channel_name}')

    channel_id = get_mllp_channel_id(page, channel_name)
    page.evaluate('channelId => $.fn.zato.channel.hl7.mllp.invoke(channelId)', channel_id)
    _wait_for_overlay(page)

    out = _invoke_in_overlay(page, message)
    return out

# ################################################################################################################################

def publish_to_topic(page:'Page', base_url:'str', topic_name:'str', payload:'str') -> 'None':
    """ Publishes a message to a topic from the Publish overlay of its row.
    """
    navigate_to_page(page, base_url, f'{_topic_page_url}?query={topic_name}')

    topic_id = get_topic_id(page, topic_name)
    open_publish_overlay(page, topic_id)
    publish_via_overlay(page, payload)

    page.evaluate('$.fn.zato.invoker.close_overlay()')

# ################################################################################################################################
# ################################################################################################################################
