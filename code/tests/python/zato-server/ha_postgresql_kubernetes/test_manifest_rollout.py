# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The readiness probe and the stop grace of the pair in the Kubernetes manifest of a rolling update.

# stdlib
import os
from string import Template

# PyYAML
import yaml

# Zato
from kube_cluster import ModuleCtx as ClusterCtx
from kube_env import ModuleCtx as EnvCtx
from nodes import Timers
from zato.server.arbiter_config import ModuleCtx as ArbiterCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The kind of the object that runs the pods of the pair
    StatefulSet_Kind = 'StatefulSet'

    # The path of the readiness probe of each pod
    Ready_Path = '/zato/ha/ready'

    # How much longer than the stop grace of the Zato server a stopping node waits for its server, in seconds,
    # the same as RELEASE_MARGIN of zato_ha_core/src/control.rs
    Release_Margin = 5.0

    # How long one request of the node to the API server may take, in seconds, under the default timers
    API_Request_Timeout = Timers().request_timeout

    # How many requests to the API server a release sends - the read of the record and its compare-and-set
    Release_Requests = 2

    # How long a releasing node may take before the kubelet kills it, in seconds
    Release_Bound = ArbiterCtx.HA_Stop_Grace + Release_Margin + Release_Requests * API_Request_Timeout

# ################################################################################################################################
# ################################################################################################################################

def _read_statefulset() -> 'anydict':
    """ Returns the StatefulSet of the pair from the rendered manifest.
    """
    path = os.path.join(ClusterCtx.Manifest_Dir, EnvCtx.Zato_Manifest)

    with open(path) as manifest_file:
        template = Template(manifest_file.read())

    # The fields of the readiness probe and of the stop grace are literals, so every placeholder may be empty.
    placeholders:'strstrdict' = {}
    for name in template.get_identifiers():
        placeholders[name] = '0'

    manifest = template.safe_substitute(placeholders)

    for document in yaml.safe_load_all(manifest):
        if document['kind'] == ModuleCtx.StatefulSet_Kind:
            return document

    raise Exception(f'No StatefulSet in {path}')

# ################################################################################################################################
# ################################################################################################################################

def test_readiness_probe_follows_the_role() -> 'None':
    """ The readiness probe of each pod uses the endpoint that answers only while the node can serve or take over,
    and the kubelet leaves a releasing node enough time to write the record.
    """
    statefulset = _read_statefulset()
    template = statefulset['spec']['template']['spec']
    container = template['containers'][0]
    probe = container['readinessProbe']['httpGet']

    assert probe['path'] == ModuleCtx.Ready_Path, f'Readiness probe path -> {probe["path"]}'

    grace = template['terminationGracePeriodSeconds']
    assert grace > ModuleCtx.Release_Bound, \
        f'terminationGracePeriodSeconds {grace} does not exceed the release bound of {ModuleCtx.Release_Bound}'

# ################################################################################################################################
# ################################################################################################################################
