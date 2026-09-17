# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The real delivery callables behind the alerting engine's action menu - built the same
# way for the sweep and for the explain service, so an alert delivers through the same
# connections whether or not the LLM explained it first.

# requests
import requests

# Zato
from zato.common.alerting.engine import AlertTransports
from zato.common.alerting.names import get_notification_conn_name
from zato.common.alerting.object_config import decode_email_connection, Email_Conn_Type_IMAP, Email_Conn_Type_SMTP
from zato.common.api import SMTPMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strlist
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# How long a webhook post may take before it is abandoned, in seconds.
Webhook_Timeout = 10

# ################################################################################################################################
# ################################################################################################################################

def build_alert_transports(service:'Service', email_from:'str') -> 'AlertTransports':
    """ Wires the delivery callables the engine dispatches through - email, Slack and
    Microsoft Teams ride on the connections that share the default notification name,
    next to the server's own invoker, pub/sub and HTTP for plain webhooks. Each callable
    returns without delivering when its connection does not exist or is inactive.
    An email about an object with an email connection of its own leaves through that
    connection instead - an SMTP one, or a Microsoft 365 one sending through Graph.
    """
    conn_name = get_notification_conn_name()
    logger = service.logger

    def send_email(addresses:'strlist', subject:'str', body:'str', email_connection:'str'='') -> 'None':

        # The email component may be disabled in server.conf.
        if not service.email:
            logger.info('Could not send an alerting email; is component_enabled.email set to True in server.conf?')
            return

        # The default notification connection is an SMTP one, an object's own names its kind itself.
        if email_connection:
            kind, name = decode_email_connection(email_connection)
        else:
            kind = Email_Conn_Type_SMTP
            name = conn_name

        if kind == Email_Conn_Type_SMTP:
            store = service.email.smtp
            kind_label = 'SMTP'
        elif kind == Email_Conn_Type_IMAP:
            store = service.email.imap
            kind_label = 'Microsoft 365'
        else:
            logger.info('Email connection `%s` is of an unknown kind, skipping an email to `%s`', email_connection, addresses)
            return

        # A connection that does not exist sends nothing ..
        try:
            item = store.get(name, True)
        except KeyError:
            logger.info('No %s connection `%s` exists, skipping an email to `%s`', kind_label, name, addresses)
            return

        # .. and neither does an inactive one.
        if not item.config['is_active']:
            logger.info('%s connection `%s` is inactive, skipping an email to `%s`', kind_label, name, addresses)
            return

        message = SMTPMessage()
        message.from_ = email_from
        message.to = addresses
        message.subject = subject
        message.body = body

        item.conn.send(message)

    def invoke_service(service_name:'str', payload:'stranydict') -> 'None':
        _ = service.server.invoke(service_name, payload)

    def publish(topic_name:'str', payload:'stranydict') -> 'None':
        _ = service.server.pubsub_backend.publish(topic_name, payload, cid=service.cid, correl_id=service.cid)

    def send_slack(channel:'str', text:'str') -> 'None':

        # A connection that does not exist or is inactive sends nothing.
        if conn_name not in service.slack.conn_dict:
            logger.info('No Slack connection `%s` exists, skipping the notification', conn_name)
            return

        item = service.slack.conn_dict[conn_name]

        if not item['is_active']:
            logger.info('Slack connection `%s` is inactive, skipping the notification', conn_name)
            return

        _ = service.slack.send(conn_name, channel, text)

    def send_teams(to:'str', html:'str') -> 'None':

        # A connection that does not exist or is inactive sends nothing.
        if conn_name not in service.microsoft.teams.conn_dict:
            logger.info('No Microsoft Teams connection `%s` exists, skipping the notification', conn_name)
            return

        item = service.microsoft.teams.conn_dict[conn_name]

        if not item['is_active']:
            logger.info('Microsoft Teams connection `%s` is inactive, skipping the notification', conn_name)
            return

        _ = service.microsoft.teams.send(conn_name, to, html)

    def http_post(url:'str', payload:'stranydict') -> 'None':
        response = requests.post(url, json=payload, timeout=Webhook_Timeout)
        if not response.ok:
            logger.warning('Alert webhook `%s` returned %s - %s', url, response.status_code, response.text)

    # Our response to produce
    out = AlertTransports()

    out.send_email = send_email
    out.invoke_service = invoke_service
    out.publish = publish
    out.send_slack = send_slack
    out.send_teams = send_teams
    out.http_post = http_post

    return out

# ################################################################################################################################
# ################################################################################################################################
