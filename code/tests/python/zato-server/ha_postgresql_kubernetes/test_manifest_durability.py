# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The manifest of the PostgreSQL instances of the Kubernetes suites, rendered with the values that the suites apply.
# Every StatefulSet with more than one PostgreSQL instance makes each commit wait for a synchronous standby.

# PyYAML
import yaml

# Zato
from kube_cluster import render_manifest
from kube_postgresql import get_manifest_placeholders, ModuleCtx as PostgreSQLCtx
from zato.common.test.pubsub_database import PubSubDatabase, PubSubDBMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The kind of the objects that run the instances
    StatefulSet_Kind = 'StatefulSet'

    # The option that precedes each setting among the arguments of an instance
    Setting_Option = '-c'

    # The setting that names the standbys each commit waits for
    Synchronous_Standby_Names = 'synchronous_standby_names'

# ################################################################################################################################
# ################################################################################################################################

def _read_settings(args:'strlist') -> 'strstrdict':
    """ Returns the settings that the arguments of an instance pass to PostgreSQL, by their names.
    """
    out:'strstrdict' = {}

    for index, arg in enumerate(args):
        if arg == ModuleCtx.Setting_Option:
            setting = args[index + 1]
            name, value = setting.split('=', 1)
            out[name] = value

    return out

# ################################################################################################################################

def _get_statefulsets() -> 'list[anydict]':
    """ Returns each StatefulSet of the rendered manifest.
    """
    database = PubSubDatabase(mode=PubSubDBMode.PostgreSQL_TLS)
    placeholders = get_manifest_placeholders(database)
    manifest = render_manifest(PostgreSQLCtx.Manifest_Path, placeholders)

    out:'list[anydict]' = []

    for document in yaml.safe_load_all(manifest):
        if document['kind'] == ModuleCtx.StatefulSet_Kind:
            out.append(document)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_every_multi_instance_configuration_is_synchronous() -> 'None':
    """ Each StatefulSet of more than one instance passes a non-empty synchronous_standby_names to each of its containers.
    """
    statefulsets = _get_statefulsets()
    assert statefulsets, f'No StatefulSet in {PostgreSQLCtx.Manifest_Path}'

    for statefulset in statefulsets:
        name = statefulset['metadata']['name']
        replicas = statefulset['spec']['replicas']

        if replicas > 1:
            for container in statefulset['spec']['template']['spec']['containers']:
                settings = _read_settings(container['args'])
                setting_name = ModuleCtx.Synchronous_Standby_Names

                assert setting_name in settings, f'StatefulSet {name} has {replicas} instances and no {setting_name}'
                assert settings[setting_name], f'StatefulSet {name} has {replicas} instances and an empty {setting_name}'

# ################################################################################################################################
# ################################################################################################################################
