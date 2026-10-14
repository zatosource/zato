# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The registry behind the Demo config screen - every set has to be importable,
# checkable and removable, the details have to say which objects exist, a save
# has to act only on the sliders that changed, and the emptiness check has to
# see through what a new environment is created with.

# stdlib
import os

# Zato
from zato.common.typing_ import cast_
from zato.server.demo_config import First_Start_Set_Names, get_demo_config_details, has_user_services, is_cluster_empty, \
    save_demo_config, Set_File_Transfer, Set_Names, _delete_generic_connections, _delete_http_soap, _delete_jobs, \
    _existing_names_funcs, _import_file_transfer, _import_funcs, _manifests, _remove_file_transfer, _remove_funcs
from zato.server.demo_file_transfer.common import Root_Env_Name
from zato.server.demo_file_transfer.layout import All_Connections, Feeder_Name, get_connection_names, \
    get_schedule_job_names

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pathlib import Path
    from pytest import MonkeyPatch
    from zato.common.typing_ import any_, anylist, strdict, strlist

    any_ = any_
    anylist = anylist
    MonkeyPatch = MonkeyPatch
    Path = Path
    strdict = strdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The pickup directory the fake server names - it never exists, so removing
# a pickup file is a no-op the tests do not have to clean up after
_pickup_dir = os.path.join('/tmp', 'zato-demo-config-test-pickup-does-not-exist')

# ################################################################################################################################
# ################################################################################################################################

class _FakeQuery:
    """ Answers a query with the rows it was built with, whatever the filters.
    """
    def __init__(self, rows:'anylist') -> 'None':
        self.rows = rows

    def filter(self, *args:'any_') -> '_FakeQuery':
        return self

    def all(self) -> 'anylist':
        return self.rows

    def count(self) -> 'int':
        out = len(self.rows)
        return out

# ################################################################################################################################

class _FakeSession:
    """ Hands out queries over dict rows prebuilt per model - a query over Job sees
    only the Job rows, one over GenericConn only the GenericConn rows and so on.
    A query over columns projects each dict row down to a tuple of just those
    columns, the way a real session answers with tuples.
    """
    def __init__(self, rows_by_model:'strdict') -> 'None':
        self.rows_by_model = rows_by_model

    def query(self, *args:'any_') -> '_FakeQuery':

        # A query is built either over a model class or over its columns -
        # a column knows the class it belongs to
        first = args[0]

        if isinstance(first, type):
            model = first
        else:
            model = first.class_

        dict_rows = self.rows_by_model.get(model.__name__, [])

        # A query over the whole model is only ever counted, so its rows go out
        # as they are - one over columns is unpacked, so its rows are projected
        if isinstance(first, type):
            rows = dict_rows
        else:
            rows = []
            for dict_row in dict_rows:
                row = tuple(dict_row[column.key] for column in args)
                rows.append(row)

        out = _FakeQuery(rows)
        return out

    def close(self) -> 'None':
        pass

# ################################################################################################################################

class _FakeODB:
    """ Hands out sessions over the prebuilt rows.
    """
    def __init__(self, rows_by_model:'strdict') -> 'None':
        self.rows_by_model = rows_by_model

    def session(self) -> '_FakeSession':
        out = _FakeSession(self.rows_by_model)
        return out

# ################################################################################################################################

class _FakeHotDeployConfig:
    """ Only the pickup directory is ever read.
    """
    def __init__(self) -> 'None':
        self.pickup_dir = _pickup_dir

# ################################################################################################################################

class _FakeServer:
    """ Records every service invocation and every demo import the registry makes.
    """
    def __init__(self, rows_by_model:'strdict | None'=None) -> 'None':

        if rows_by_model is None:
            rows_by_model = {}

        self.name = 'test.demo.config.server'
        self.odb = _FakeODB(rows_by_model)
        self.hot_deploy_config = _FakeHotDeployConfig()

        self.service_sources:'anylist' = []
        self.deploy_auto_from = ''

        self.invoked:'anylist' = []
        self.imported:'strlist' = []

    def invoke(self, service:'str', request:'any_') -> 'None':
        self.invoked.append((service, request))

    def import_demo_scheduler(self) -> 'bool':
        self.imported.append('scheduler')
        return True

    def import_demo_tutorial(self) -> 'bool':
        self.imported.append('tutorial')
        return True

    def import_demo_hl7(self) -> 'bool':
        self.imported.append('hl7')
        return True

    def import_demo_ibm_mq(self) -> 'bool':
        self.imported.append('ibm_mq')
        return True

    def import_demo_kafka(self) -> 'bool':
        self.imported.append('kafka')
        return True

    def import_demo_pubsub(self) -> 'bool':
        self.imported.append('pubsub')
        return True

    def import_demo_file_transfer(self) -> 'bool':
        self.imported.append('file_transfer')
        return True

# ################################################################################################################################
# ################################################################################################################################

def _build_states(**overrides:'bool') -> 'strdict':
    """ A full set of slider states, every set off unless an override says otherwise.
    """

    # Our response to produce
    out:'strdict' = {}

    for set_name in Set_Names:
        out[set_name] = False

    out.update(overrides)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRegistryIsComplete:

    def test_every_set_has_a_manifest_and_both_funcs(self):

        for set_name in Set_Names:
            assert set_name in _manifests, f'No manifest for: {set_name}'
            assert set_name in _import_funcs, f'No import func for: {set_name}'
            assert set_name in _remove_funcs, f'No remove func for: {set_name}'

    def test_every_manifest_kind_has_a_lookup_func(self):

        for set_name in Set_Names:
            for manifest_group in _manifests[set_name]:
                kind = manifest_group['kind']
                assert kind in _existing_names_funcs, f'No lookup func for: {kind} (set: {set_name})'
                assert manifest_group['names'], f'No names for: {kind} (set: {set_name})'

    def test_every_first_start_set_is_registered(self):

        for set_name in First_Start_Set_Names:
            assert set_name in Set_Names, f'Not a known set: {set_name}'
            assert set_name in _import_funcs, f'No import func for: {set_name}'

# ################################################################################################################################
# ################################################################################################################################

class TestGetDemoConfigDetails:

    def test_details_show_what_exists(self):

        # Only the Kafka connections exist ..
        rows_by_model = {
            'GenericConn': [
                {'id': 111, 'name': 'demo.kafka.channel'},
                {'id': 222, 'name': 'demo.kafka.publisher'},
            ],
        }

        server = _FakeServer(rows_by_model)
        out = get_demo_config_details(server) # type: ignore[arg-type]

        sets = out['sets']

        # .. so the Kafka set is present and each of its objects exists ..
        assert sets['kafka']['is_present'] is True

        for group in sets['kafka']['groups']:
            for item in group['items']:
                assert item['exists'] is True, f'Expected an existing item: {item}'

        # .. and the scheduler set is absent and none of its objects exist.
        assert sets['scheduler']['is_present'] is False

        for group in sets['scheduler']['groups']:
            for item in group['items']:
                assert item['exists'] is False, f'Expected a missing item: {item}'

# ################################################################################################################################
# ################################################################################################################################

class TestDeleteHelpers:

    def test_delete_jobs_deletes_each_row_by_id(self):

        rows_by_model = {
            'Job': [
                {'id': 111, 'name': 'crm.sync-contacts'},
                {'id': 222, 'name': 'crm.sync-accounts'},
            ],
        }

        server = _FakeServer(rows_by_model)
        out = _delete_jobs(server, ['crm.sync-contacts', 'crm.sync-accounts']) # type: ignore[arg-type]

        assert out == ['crm.sync-contacts', 'crm.sync-accounts']
        assert server.invoked == [
            ('zato.scheduler.job.delete', {'id': 111}),
            ('zato.scheduler.job.delete', {'id': 222}),
        ]

    def test_delete_generic_connections_deletes_each_row_by_id(self):

        rows_by_model = {
            'GenericConn': [
                {'id': 111, 'name': 'demo.kafka.channel'},
                {'id': 222, 'name': 'demo.kafka.publisher'},
            ],
        }

        connections = [
            ('demo.kafka.channel', 'channel-kafka'),
            ('demo.kafka.publisher', 'outconn-kafka'),
        ]

        server = _FakeServer(rows_by_model)
        out = _delete_generic_connections(server, connections) # type: ignore[arg-type]

        assert out == ['demo.kafka.channel', 'demo.kafka.publisher']

        assert len(server.invoked) == 2

        for service, request in server.invoked:
            assert service == 'zato.generic.connection.delete'
            assert request['id'] in (111, 222)

    def test_delete_http_soap_deletes_each_row_by_id(self):

        rows_by_model = {
            'HTTPSOAP': [
                {'id': 111, 'name': 'My REST Channel'},
            ],
        }

        server = _FakeServer(rows_by_model)
        out = _delete_http_soap(server, 'My REST Channel', 'channel') # type: ignore[arg-type]

        assert out == ['My REST Channel']
        assert server.invoked == [
            ('zato.http-soap.delete', {'id': 111}),
        ]

# ################################################################################################################################
# ################################################################################################################################

class TestSaveDemoConfig:

    def test_no_changes_reports_nothing_to_apply(self):

        # An empty environment and every slider off - nothing differs
        server = _FakeServer()
        states = _build_states()

        out = save_demo_config(server, states) # type: ignore[arg-type]

        assert out['success'] is True
        assert out['message'] == 'No changes to apply'
        assert server.imported == []
        assert server.invoked == []

        for set_name in Set_Names:
            assert out['results'][set_name] == {'action': 'unchanged', 'is_ok': True}

    def test_a_slider_slid_on_imports_its_set(self):

        # An empty environment and the scheduler slider on - one import runs
        server = _FakeServer()
        states = _build_states(scheduler=True)

        out = save_demo_config(server, states) # type: ignore[arg-type]

        assert out['success'] is True
        assert out['message'] == 'Imported: scheduler'
        assert server.imported == ['scheduler']

        assert out['results']['scheduler'] == {'action': 'imported', 'is_ok': True}

    def test_a_slider_slid_off_removes_its_set(self):

        # The Kafka connections exist and their slider goes off, so only their
        # objects are removed - every other set is absent and stays off
        rows_by_model = {
            'GenericConn': [
                {'id': 111, 'name': 'demo.kafka.channel'},
                {'id': 222, 'name': 'demo.kafka.publisher'},
            ],
        }

        server = _FakeServer(rows_by_model)
        states = _build_states(kafka=False)

        out = save_demo_config(server, states) # type: ignore[arg-type]

        assert out['success'] is True
        assert out['message'] == 'Removed: kafka'
        assert server.imported == []

        assert out['results']['kafka'] == {'action': 'removed', 'is_ok': True}
        assert out['results']['hl7'] == {'action': 'unchanged', 'is_ok': True}
        assert out['results']['ibm_mq'] == {'action': 'unchanged', 'is_ok': True}

        assert len(server.invoked) == 2

        for service, request in server.invoked:
            assert service == 'zato.generic.connection.delete'
            assert request['id'] in (111, 222)

# ################################################################################################################################
# ################################################################################################################################

class TestIsClusterEmpty:

    def test_a_new_environment_is_empty(self):

        server = _FakeServer()
        assert is_cluster_empty(server) is True # type: ignore[arg-type]

    def test_a_scheduler_job_makes_it_non_empty(self):

        rows_by_model = {
            'Job': [
                {'id': 111, 'name': 'my.report.job'},
            ],
        }

        server = _FakeServer(rows_by_model)
        assert is_cluster_empty(server) is False # type: ignore[arg-type]

    def test_a_channel_makes_it_non_empty(self):

        rows_by_model = {
            'HTTPSOAP': [
                {'id': 111, 'name': 'my.channel'},
            ],
        }

        server = _FakeServer(rows_by_model)
        assert is_cluster_empty(server) is False # type: ignore[arg-type]

    def test_a_pubsub_topic_makes_it_non_empty(self):

        rows_by_model = {
            'PubSubTopic': [
                {'id': 111, 'name': 'my.topic'},
            ],
        }

        server = _FakeServer(rows_by_model)
        assert is_cluster_empty(server) is False # type: ignore[arg-type]

# ################################################################################################################################
# ################################################################################################################################

class TestHasUserServices:

    def test_a_fresh_server_has_none(self):

        server = _FakeServer()
        assert has_user_services(server) is False # type: ignore[arg-type]

    def test_a_hot_deployment_source_counts(self):

        server = _FakeServer()
        server.service_sources = [os.path.join('/opt', 'my-project', 'src')]

        assert has_user_services(server) is True # type: ignore[arg-type]

    def test_an_auto_deployment_directory_counts(self):

        server = _FakeServer()
        server.deploy_auto_from = os.path.join('/opt', 'my-project')

        assert has_user_services(server) is True # type: ignore[arg-type]

    def test_a_file_in_the_pickup_directory_counts(self, tmp_path:'Path'):

        # A service file is already waiting in the pickup directory ..
        pickup_file = tmp_path / 'my_service.py'
        _ = pickup_file.write_text('class MyService: pass')

        # .. so the server has user services to deploy.
        server = _FakeServer()
        server.hot_deploy_config.pickup_dir = str(tmp_path)

        assert has_user_services(server) is True # type: ignore[arg-type]

# ################################################################################################################################
# ################################################################################################################################

class TestFileTransferSet:

    def test_the_manifest_lists_jobs_then_each_protocol(self):

        groups = _manifests[Set_File_Transfer]

        kinds = []
        for group in groups:
            kinds.append(group['kind'])

        assert kinds == ['job', 'outconn-sftp', 'outconn-ftp', 'outconn-smb']

        # The feeder job comes first, followed by one job per schedule of each connection ..
        job_names = groups[0]['names']
        assert job_names[0] == Feeder_Name
        assert job_names[1:] == get_schedule_job_names()
        assert len(job_names) == 13

        # .. and each protocol has its pair of connections.
        assert groups[1]['names'] == ['demo.sftp.acme', 'demo.sftp.globex']
        assert groups[2]['names'] == ['demo.ftp.initech', 'demo.ftps.umbrella']
        assert groups[3]['names'] == ['demo.smb.hooli', 'demo.smb.wonka']

    def test_the_set_is_registered_but_not_imported_on_first_start(self):

        assert Set_File_Transfer in Set_Names
        assert Set_File_Transfer not in First_Start_Set_Names

        assert _import_funcs[Set_File_Transfer] is _import_file_transfer
        assert _remove_funcs[Set_File_Transfer] is _remove_file_transfer

    def test_the_feeder_job_is_the_presence_check(self):

        # Only the feeder job exists ..
        rows_by_model = {
            'Job': [
                {'id': 111, 'name': Feeder_Name},
            ],
        }

        server = _FakeServer(rows_by_model)
        server_any = cast_('any_', server)

        out = get_demo_config_details(server_any)

        # .. which is what makes the set present.
        assert out['sets'][Set_File_Transfer]['is_present'] is True

    def test_a_schedule_job_alone_is_not_presence(self):

        # A job of one schedule exists but the feeder job does not ..
        rows_by_model = {
            'Job': [
                {'id': 111, 'name': 'sftp.demo.sftp.acme.invoices'},
            ],
        }

        server = _FakeServer(rows_by_model)
        server_any = cast_('any_', server)

        out = get_demo_config_details(server_any)

        # .. so the set is not present.
        assert out['sets'][Set_File_Transfer]['is_present'] is False

    def test_a_slider_slid_on_imports_the_set(self):

        server = _FakeServer()
        server_any = cast_('any_', server)

        states = _build_states(file_transfer=True)
        out = save_demo_config(server_any, states)

        assert out['success'] is True
        assert out['message'] == 'Imported: file_transfer'
        assert server.imported == ['file_transfer']

    def test_removal_deletes_the_feeder_and_the_connections(self, tmp_path:'Path', monkeypatch:'MonkeyPatch'):

        # The demo's root is a directory of this test's own ..
        root = tmp_path / 'demo-root'
        root.mkdir()

        marker_file = root / 'marker.txt'
        _ = marker_file.write_text('marker')

        monkeypatch.setenv(Root_Env_Name, str(root))

        # .. the feeder job and all the connections exist ..
        connection_rows = []

        connection_names = get_connection_names(All_Connections)

        for index, name in enumerate(connection_names):
            row = {'id': 1000 + index, 'name': name, 'type_': '', 'address': '', 'port': 0}
            connection_rows.append(row)

        rows_by_model = {
            'Job': [
                {'id': 111, 'name': Feeder_Name},
            ],
            'GenericConn': connection_rows,
        }

        server = _FakeServer(rows_by_model)
        server_any = cast_('any_', server)

        out = _remove_file_transfer(server_any)

        # .. each of them is deleted through its own service ..
        expected_deleted = {Feeder_Name}
        expected_deleted.update(get_connection_names(All_Connections))

        assert set(out['deleted']) == expected_deleted

        invoked_services = set()
        deleted_connection_ids = set()

        for service, request in server.invoked:
            invoked_services.add(service)
            if service == 'zato.generic.connection.delete':
                deleted_connection_ids.add(request['id'])

        assert invoked_services == {'zato.scheduler.job.delete', 'zato.generic.connection.delete'}
        assert len(deleted_connection_ids) == 6

        # .. and the root is gone with everything in it.
        assert not root.exists()

# ################################################################################################################################
# ################################################################################################################################
