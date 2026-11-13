# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoints of the Service of the pair, read every 100 milliseconds throughout a run. The Service must never list
# more than one pod, and each period in which it lists none is measured.

# stdlib
import logging
import threading
import time
from urllib.error import URLError

# Zato
from kube_cluster import ModuleCtx as ClusterCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_cluster import KubeProxy
    from zato.common.typing_ import any_, strlist

    KubeProxy = KubeProxy

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite_kubernetes.endpoints')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The Service of the pair
    Service_Name = 'zato-ha'

    # How often the endpoints are read, in seconds
    Poll_Interval = 0.1

# ################################################################################################################################
# ################################################################################################################################

def get_ready_pods(slices:'any_') -> 'strlist':
    """ Returns the pods that the endpoint slices of a Service list as ready, which are the ones it routes to.
    """
    out:'strlist' = []

    for endpoint_slice in slices['items']:

        # A slice of a Service without endpoints has no list of them.
        if not endpoint_slice['endpoints']:
            continue

        for endpoint in endpoint_slice['endpoints']:
            if endpoint['conditions']['ready']:
                pod_name = endpoint['targetRef']['name']
                if pod_name not in out:
                    out.append(pod_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

class EndpointWatcher:
    """ Reads the ready endpoints of the Service of the pair in a thread of its own and records each time
    it listed more than one pod and each period in which it listed none.
    """

    def __init__(self, proxy:'KubeProxy') -> 'None':
        self.proxy = proxy
        self.lock = threading.Lock()
        self.is_running = threading.Event()
        self.multiple:'strlist' = []
        self.empty_periods:'list[tuple[float, float]]' = []
        self._empty_since = 0.0
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._path = f'/apis/discovery.k8s.io/v1/namespaces/{ClusterCtx.Namespace}/endpointslices' + \
            f'?labelSelector=kubernetes.io/service-name={ModuleCtx.Service_Name}'

    def start(self) -> 'None':
        self.is_running.set()
        self._thread.start()

    def stop(self) -> 'None':
        self.is_running.clear()
        self._thread.join()

    def get_empty_periods_after(self, start:'float') -> 'list[tuple[float, float]]':
        """ Returns each period after the given time in which the Service listed no pod.
        """
        out:'list[tuple[float, float]]' = []

        with self.lock:
            for period_start, period_end in self.empty_periods:
                if period_end >= start:
                    out.append((period_start, period_end))

        return out

    def _run(self) -> 'None':

        while self.is_running.is_set():
            now = time.time()

            # The API server may not answer for a moment, which is not a reading of the endpoints.
            try:
                slices = self.proxy.get(self._path)
            except (URLError, OSError):
                time.sleep(ModuleCtx.Poll_Interval)
                continue

            pods = get_ready_pods(slices)

            with self.lock:

                if len(pods) > 1:
                    self.multiple.append(f'{now:.3f} {pods}')
                    logger.warning('Service lists more than one pod -> %s', pods)

                # A period without pods begins ..
                if not pods:
                    if not self._empty_since:
                        self._empty_since = now

                # .. and ends once a pod is listed again.
                elif self._empty_since:
                    self.empty_periods.append((self._empty_since, now))
                    logger.info('Service listed no pod for %.1fs', now - self._empty_since)
                    self._empty_since = 0.0

            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################
