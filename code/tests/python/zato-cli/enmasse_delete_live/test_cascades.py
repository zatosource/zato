# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import NOT_FOUND

# Zato
from zato.cli.enmasse.importer.delete_targets import http_soap_sections
from zato.common.defaults import default_cluster_id

# Zato - the suite's own parts
from _definitions import basic_auth, deletion_file, group, marked, outgoing_rest, permission, Ping_Service, Prefix, \
    quota_tier, rate_limiting_rules, rest_channel, subscription, topic
from _support import is_listed, is_served, job_names, listed_names, ModuleCtx as SupportCtx, Pickup, Runtime, url_status

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What the quota tier delete service answers while anything references the tier
    Tier_Referenced = 'still referenced by'

    # When the jobs of the dependent jobs test first run
    Scheduler_Start_Date = '2030-01-01T00:00:00'

    # How many jobs the owning objects of the dependent jobs test create - the IMAP job, three schedule jobs,
    # the FHIR health check and bulk export jobs and the outgoing REST invocation job
    Dependent_Job_Count = 7

# ################################################################################################################################
# ################################################################################################################################

def _names(prefix:'str', *parts:'str') -> 'anydict':
    """ The names of the objects of one test, each under the test's own prefix.
    """
    out = {part: f'{Prefix}{prefix}.{part}' for part in parts}
    return out

# ################################################################################################################################

def _url_path(prefix:'str', part:'str') -> 'str':
    """ The URL path of one channel of a test.
    """
    out = '/' + Prefix.replace('.', '/') + f'{prefix}/{part}'
    return out

# ################################################################################################################################

def _new_names(before:'strlist', after:'strlist') -> 'strlist':
    """ The names present after a step that were not present before it.
    """
    out = sorted(set(after) - set(before))
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_security_cascade(
    environment:'ZatoEnvironment',
    client:'AdminClient',
    pickup:'Pickup',
    runtime:'Runtime',
    ) -> 'None':
    """ Deleting a security definition alone takes the channel, the outgoing connection, the permission and
    the subscription that use it along with it.
    """
    names = _names('cascade', 'security', 'channel', 'outgoing', 'topic')
    username = 'enmasse.delete.live.cascade'
    url_path = _url_path('cascade', 'channel')

    config = {
        'security':            [basic_auth(names['security'], username)],
        'pubsub_topic':        [topic(names['topic'])],
        'channel_rest':        [rest_channel(names['channel'], url_path, security=names['security'])],
        'outgoing_rest':       [outgoing_rest(names['outgoing'], security=names['security'])],
        'pubsub_permission':   [permission(names['security'], [names['topic']])],
        'pubsub_subscription': [subscription(names['security'], [names['topic']])],
    }

    # Everything is created ..
    log = pickup.place('cascade-create', config)
    assert SupportCtx.Import_OK in log, log

    assert url_status(environment, url_path) != NOT_FOUND
    assert runtime.is_present('outgoing_rest', names['outgoing'])
    assert runtime.is_present('pubsub_permission', username, names['topic'])
    assert runtime.is_present('pubsub_subscription', username, names['topic'])

    # .. the security definition alone is deleted ..
    log = pickup.place('cascade-delete', deletion_file('security', names['security']))
    assert SupportCtx.Import_OK in log, log

    # .. and nothing that used it is left.
    assert url_status(environment, url_path) == NOT_FOUND
    assert not is_listed(client, runtime, 'channel_rest', names['channel'])

    assert not is_listed(client, runtime, 'outgoing_rest', names['outgoing'])
    assert not runtime.is_present('outgoing_rest', names['outgoing'])

    assert not is_listed(client, runtime, 'pubsub_permission', names['security'])
    assert not runtime.is_present('pubsub_permission', username, names['topic'])

    assert not is_listed(client, runtime, 'pubsub_subscription', names['security'])
    assert not runtime.is_present('pubsub_subscription', username, names['topic'])

# ################################################################################################################################

def test_group_deletion(
    environment:'ZatoEnvironment',
    client:'AdminClient',
    pickup:'Pickup',
    runtime:'Runtime',
    ) -> 'None':
    """ Deleting a group removes it from the security groups of a REST channel, which continues to serve.
    """
    names = _names('group', 'security', 'group', 'channel')
    url_path = _url_path('group', 'channel')

    config = {
        'security':     [basic_auth(names['security'], 'enmasse.delete.live.group')],
        'groups':       [group(names['group'], [names['security']])],
        'channel_rest': [rest_channel(names['channel'], url_path, groups=[names['group']])],
    }

    # The channel is guarded by the group ..
    log = pickup.place('group-create', config)
    assert SupportCtx.Import_OK in log, log

    assert _security_group_count(client, names['channel']) == 1
    assert not is_served(environment, url_path)

    # .. the group is deleted ..
    log = pickup.place('group-delete', deletion_file('groups', names['group']))
    assert SupportCtx.Import_OK in log, log

    # .. and the channel has no group left and serves.
    assert not is_listed(client, runtime, 'groups', names['group'])
    assert _security_group_count(client, names['channel']) == 0
    assert is_served(environment, url_path)

# ################################################################################################################################

def _security_group_count(client:'AdminClient', channel_name:'str') -> 'int':
    """ How many security groups the server reports for a REST channel.
    """
    connection, transport = http_soap_sections['channel_rest']
    items, _ = client.get_list('zato.http-soap.get-list',
        cluster_id=default_cluster_id, connection=connection, transport=transport)

    for item in items:
        if item['name'] == channel_name:
            out = item['security_group_count']
            return out

    raise Exception(f'Channel `{channel_name}` not found')

# ################################################################################################################################

def test_topic_deletion(client:'AdminClient', pickup:'Pickup', runtime:'Runtime') -> 'None':
    """ Deleting a topic removes a subscription left without topics and keeps one that has other topics.
    """
    names = _names('topic', 'first_security', 'second_security', 'first_topic', 'second_topic')
    first_username = 'enmasse.delete.live.topic.first'
    second_username = 'enmasse.delete.live.topic.second'

    topics = [names['first_topic'], names['second_topic']]

    config = {
        'security': [
            basic_auth(names['first_security'], first_username),
            basic_auth(names['second_security'], second_username),
        ],
        'pubsub_topic': [topic(names['first_topic']), topic(names['second_topic'])],
        'pubsub_permission': [
            permission(names['first_security'], topics),
            permission(names['second_security'], [names['first_topic']]),
        ],
        'pubsub_subscription': [
            subscription(names['first_security'], topics),
            subscription(names['second_security'], [names['first_topic']]),
        ],
    }

    # Two subscriptions, one on both topics and one on the first alone ..
    log = pickup.place('topic-create', config)
    assert SupportCtx.Import_OK in log, log

    assert runtime.is_present('pubsub_subscription', first_username, names['first_topic'])
    assert runtime.is_present('pubsub_subscription', second_username, names['first_topic'])

    # .. the first topic is deleted ..
    log = pickup.place('topic-delete', deletion_file('pubsub_topic', names['first_topic']))
    assert SupportCtx.Import_OK in log, log

    # .. the subscription that had the first topic alone is gone ..
    assert not is_listed(client, runtime, 'pubsub_subscription', names['second_security'])
    assert not runtime.is_present('pubsub_subscription', second_username)

    # .. and the other one keeps its second topic.
    assert is_listed(client, runtime, 'pubsub_subscription', names['first_security'])
    assert runtime.is_present('pubsub_subscription', first_username, names['second_topic'])
    assert not runtime.is_present('pubsub_subscription', first_username, names['first_topic'])

# ################################################################################################################################

def test_permission_deletion(client:'AdminClient', pickup:'Pickup', runtime:'Runtime') -> 'None':
    """ Deleting the permissions of a security definition removes the topics they covered from its subscription,
    and a subscription left without topics with them.
    """
    names = _names('permission', 'security', 'first_topic', 'second_topic')
    username = 'enmasse.delete.live.permission'
    topics = [names['first_topic'], names['second_topic']]

    config = {
        'security':            [basic_auth(names['security'], username)],
        'pubsub_topic':        [topic(names['first_topic']), topic(names['second_topic'])],
        'pubsub_permission':   [permission(names['security'], topics)],
        'pubsub_subscription': [subscription(names['security'], topics)],
    }

    # A subscription on two topics the permission covers ..
    log = pickup.place('permission-create', config)
    assert SupportCtx.Import_OK in log, log

    assert runtime.is_present('pubsub_subscription', username, names['first_topic'])
    assert runtime.is_present('pubsub_subscription', username, names['second_topic'])

    # .. the permission is deleted ..
    log = pickup.place('permission-delete', deletion_file('pubsub_permission', names['security']))
    assert SupportCtx.Import_OK in log, log

    # .. and no topic of the subscription is covered any longer, so the subscription is gone.
    assert not is_listed(client, runtime, 'pubsub_permission', names['security'])
    assert not is_listed(client, runtime, 'pubsub_subscription', names['security'])

    assert not runtime.is_present('pubsub_permission', username, names['first_topic'])
    assert not runtime.is_present('pubsub_subscription', username, names['first_topic'])
    assert not runtime.is_present('pubsub_subscription', username, names['second_topic'])

# ################################################################################################################################

def test_quota_tier(client:'AdminClient', pickup:'Pickup', runtime:'Runtime') -> 'None':
    """ A quota tier is refused while a security definition outside the file references it, and deleted once
    the same file updates that definition to rules of its own.
    """
    names = _names('tier', 'tier', 'security')
    username = 'enmasse.delete.live.tier'

    security = basic_auth(names['security'], username)
    security['quota_tier'] = names['tier']

    config = {
        'quota_tier': [quota_tier(names['tier'])],
        'security':   [security],
    }

    # The tier and a definition following it ..
    log = pickup.place('tier-create', config)
    assert SupportCtx.Import_OK in log, log
    assert is_listed(client, runtime, 'quota_tier', names['tier'])

    # .. the tier alone cannot go ..
    log = pickup.place('tier-refused', deletion_file('quota_tier', names['tier']))
    assert SupportCtx.Import_Error in log, log
    assert ModuleCtx.Tier_Referenced in log, log
    assert is_listed(client, runtime, 'quota_tier', names['tier'])

    # .. and it goes once the definition has rules of its own.
    security = basic_auth(names['security'], username)
    security['rate_limiting'] = rate_limiting_rules()

    config = {
        'security':   [security],
        'quota_tier': [marked('quota_tier', names['tier'])],
    }

    log = pickup.place('tier-delete', config)
    assert SupportCtx.Import_OK in log, log

    assert not is_listed(client, runtime, 'quota_tier', names['tier'])
    assert not runtime.is_present('quota_tier', names['tier'])
    assert is_listed(client, runtime, 'security', names['security'])

# ################################################################################################################################

def test_dependent_jobs(client:'AdminClient', pickup:'Pickup') -> 'None':
    """ The jobs that owning objects create are removed along with those objects - the IMAP job, the file transfer
    schedule jobs, the FHIR health check and bulk export jobs and the outgoing REST invocation job.
    """
    names = _names('dependent', 'imap', 'sftp', 'smb', 'ftp', 'fhir', 'outgoing')

    schedule = {
        'name': 'enmasse.delete.live.schedule',
        'directory': '/incoming',
        'pattern': '*.csv',
        'service': Ping_Service,
        'run_every': 10,
        'run_unit': 'minutes',
    }

    config = {
        'email_imap': [{
            'name': names['imap'],
            'host': 'imap.example.com',
            'port': 993,
            'username': 'enmasse@example.com',
            'password': 'Zato_Enmasse_Delete_Live_Password_28',
            'is_active': False,
            'scheduler_run_every': 5,
            'scheduler_run_unit': 'minutes',
            'scheduler_start_date': ModuleCtx.Scheduler_Start_Date,
            'scheduler_service': Ping_Service,
        }],
        'sftp': [{
            'name': names['sftp'],
            'address': 'sftp.example.com:22',
            'username': 'enmasse',
            'password': 'Zato_Enmasse_Delete_Live_Password_29',
            'is_active': False,
            'schedules': [schedule],
        }],
        'smb': [{
            'name': names['smb'],
            'host': 'smb.example.com',
            'port': 445,
            'username': 'enmasse',
            'password': 'Zato_Enmasse_Delete_Live_Password_30',
            'is_active': False,
            'schedules': [dict(schedule, directory='Share/incoming')],
        }],
        'ftp': [{
            'name': names['ftp'],
            'host': 'ftp.example.com',
            'port': 21,
            'username': 'enmasse',
            'password': 'Zato_Enmasse_Delete_Live_Password_31',
            'is_active': False,
            'schedules': [schedule],
        }],
        'outgoing_fhir': [{
            'name': names['fhir'],
            'address': 'https://fhir.example.com/r4',
            'is_active': False,
            'health_check_run_every': 5,
            'health_check_run_unit': 'minutes',
            'bulk_export': {
                'is_active': False,
                'level': 'system',
                'run_every': 1,
                'run_unit': 'days',
                'start_date': ModuleCtx.Scheduler_Start_Date,
            },
        }],
        'outgoing_rest': [outgoing_rest(names['outgoing'],
            scheduler_run_every=10, scheduler_run_unit='minutes', scheduler_start_date=ModuleCtx.Scheduler_Start_Date)],
    }

    jobs_before = job_names(client)

    # The owning objects are created with the jobs that come with them ..
    log = pickup.place('dependent-create', config)
    assert SupportCtx.Import_OK in log, log

    new_jobs = _new_names(jobs_before, job_names(client))
    assert len(new_jobs) == ModuleCtx.Dependent_Job_Count, new_jobs

    # .. the owning objects are deleted ..
    config = {
        'email_imap':    [marked('email_imap', names['imap'])],
        'sftp':          [marked('sftp', names['sftp'])],
        'smb':           [marked('smb', names['smb'])],
        'ftp':           [marked('ftp', names['ftp'])],
        'outgoing_fhir': [marked('outgoing_fhir', names['fhir'])],
        'outgoing_rest': [marked('outgoing_rest', names['outgoing'])],
    }

    log = pickup.place('dependent-delete', config)
    assert SupportCtx.Import_OK in log, log

    # .. and none of the jobs that came with them is left.
    remaining = sorted(set(new_jobs) & set(job_names(client)))
    assert not remaining, remaining

    for section, name in (('email_imap', names['imap']), ('outgoing_rest', names['outgoing'])):
        assert name not in listed_names(client, section), f'{section} `{name}` is still listed'

# ################################################################################################################################
# ################################################################################################################################
