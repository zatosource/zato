# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time
from collections import deque
from dataclasses import dataclass
from http.client import OK
from urllib.parse import urlencode

# Zato
from zato_deploy.common import anydict, floatnone, Stage_ID, StageFailed, strnone
from zato_deploy.docker_api import DockerConnection
from zato_deploy.state import Download, Progress, Stage

# ################################################################################################################################
# ################################################################################################################################

_Unit           = 'MB'
_Bytes_Per_Unit = 1_000_000

# How much of the stage the download takes, the rest being the extraction, which takes longer than the download on Azure.
_Download_Share = 0.4

# The download rate is averaged over this many seconds.
_Rate_Window = 3.0

# The stage is updated at most this often, however many messages Docker sends.
_Update_Interval = 0.25

# How often the log says that a layer is still being extracted.
_Extract_Log_Interval = 5

# How long to wait for the next message from Docker.
_Read_Timeout = 600

_Default_Tag = 'latest'

# The unit that Docker gives the progress of an extraction in, which is the seconds it has taken so far.
_Seconds_Unit = 's'

# ################################################################################################################################
# ################################################################################################################################

class _Layer_Status:
    Downloading       = 'Downloading'
    Verifying         = 'Verifying Checksum'
    Download_Complete = 'Download complete'
    Extracting        = 'Extracting'
    Pull_Complete     = 'Pull complete'
    Already_Exists    = 'Already exists'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Layer:
    current:         int
    total:           int
    is_downloaded:   bool
    is_extracted:    bool
    last_status:     str
    extract_seconds: int
    logged_seconds:  int

# ################################################################################################################################

strlayerdict = dict[str, Layer]
rate_samples = deque[tuple[float, int]]

# ################################################################################################################################
# ################################################################################################################################

class PullTracker:
    """ Turns the messages that Docker sends during a pull into the progress of the stage and its log.
    """
    def __init__(self, progress:'Progress', stage:'Stage') -> 'None':

        self.progress    = progress
        self.stage       = stage
        self.last_update = 0.0

        self.layers:  'strlayerdict' = {}
        self.samples: 'rate_samples' = deque()

        self.extracting:'Layer | None' = None

# ################################################################################################################################

    def handle(self, message:'anydict') -> 'None':

        # A pull that fails says why in the message ..
        if error := message.get('error'):
            raise StageFailed(error)

        status:'str' = message['status']
        layer_id = message.get('id')

        # .. messages that are not about a single layer go to the log as they are ..
        if layer_id is None:
            kind = 'ok' if status.startswith('Status:') else None
            self.progress.log(status, kind)
            return

        # .. and so does the name of the image being pulled, which Docker reports under the tag ..
        if status.startswith('Pulling from'):
            self.progress.log(f'{layer_id}: {status}')
            return

        # .. while each layer is tracked on its own ..
        self.update_layer(layer_id, status, message)

        # .. and the stage shows the sum of them all.
        now = time.monotonic()
        if now - self.last_update >= _Update_Interval:
            self.update_stage(now)
            self.last_update = now

# ################################################################################################################################

    def get_layer(self, layer_id:'str') -> 'Layer':

        if layer := self.layers.get(layer_id):
            return layer

        out = Layer()
        out.current         = 0
        out.total           = 0
        out.is_downloaded   = False
        out.is_extracted    = False
        out.last_status     = ''
        out.extract_seconds = 0
        out.logged_seconds  = 0

        self.layers[layer_id] = out
        return out

# ################################################################################################################################

    def update_layer(self, layer_id:'str', status:'str', message:'anydict') -> 'None':

        layer = self.get_layer(layer_id)
        detail:'anydict' = message.get('progressDetail') or {}

        # Docker reports the size of a layer before it starts downloading it ..
        if total := detail.get('total'):
            if status == _Layer_Status.Downloading:
                layer.total = total
                layer.current = detail['current']
            elif not layer.is_downloaded:
                layer.total = total

        # .. and says when it has it all ..
        if status in (_Layer_Status.Verifying, _Layer_Status.Download_Complete):
            layer.is_downloaded = True
            layer.current = layer.total

        # .. then how many seconds it has been extracting it for, since its size on disk is not known up front ..
        elif status == _Layer_Status.Extracting:
            layer.is_downloaded = True
            layer.current = layer.total
            self.extracting = layer
            if detail.get('units') == _Seconds_Unit:
                layer.extract_seconds = detail['current']

        # .. and when it is extracted ..
        elif status == _Layer_Status.Pull_Complete:
            layer.is_downloaded = True
            layer.is_extracted  = True
            layer.current = layer.total

        # .. while a layer from an earlier pull needs neither.
        elif status == _Layer_Status.Already_Exists:
            layer.is_downloaded = True
            layer.is_extracted  = True
            layer.current = 0
            layer.total   = 0

        self.log_layer(layer_id, layer, status)

# ################################################################################################################################

    def log_layer(self, layer_id:'str', layer:'Layer', status:'str') -> 'None':
        """ Logs each new status of a layer once, and every few seconds that it is still being extracted.
        """
        size = layer.total / _Bytes_Per_Unit

        if status != layer.last_status:
            layer.last_status = status

            if status == _Layer_Status.Extracting:
                self.progress.log(f'{layer_id}: Extracting {size:.1f} {_Unit}')

            elif status == _Layer_Status.Pull_Complete:
                if layer.extract_seconds:
                    self.progress.log(f'{layer_id}: Pull complete, extracted in {layer.extract_seconds}s')
                else:
                    self.progress.log(f'{layer_id}: Pull complete')

            else:
                self.progress.log(f'{layer_id}: {status}')

            return

        if status == _Layer_Status.Extracting:
            if layer.extract_seconds - layer.logged_seconds >= _Extract_Log_Interval:
                layer.logged_seconds = layer.extract_seconds
                self.progress.log(f'{layer_id}: Extracting {size:.1f} {_Unit}, {layer.extract_seconds}s')

# ################################################################################################################################

    def get_rate(self, now:'float', current:'int') -> 'floatnone':
        """ Returns the bytes per second over the last few seconds, or None before there are enough of them.
        """
        self.samples.append((now, current))

        while True:
            oldest_time, _ = self.samples[0]
            if now - oldest_time <= _Rate_Window:
                break
            _ = self.samples.popleft()

        oldest_time, oldest_current = self.samples[0]
        elapsed = now - oldest_time

        if elapsed < 1:
            return None

        out = (current - oldest_current) / elapsed
        return out

# ################################################################################################################################

    def get_extract_detail(self, extracted_count:'int', layer_count:'int') -> 'strnone':
        """ Returns which layer is being extracted and for how long, or None if none is.
        """
        layer = self.extracting

        if not layer:
            return None

        if layer.is_extracted:
            return None

        layer_number = min(extracted_count + 1, layer_count)

        out = f'Extracting {layer_number} / {layer_count}, {layer.extract_seconds}s'
        return out

# ################################################################################################################################

    def update_stage(self, now:'float') -> 'None':

        current = 0
        total = 0
        extracted_bytes = 0
        extracted_count = 0
        is_all_downloaded = True

        for layer in self.layers.values():
            current += layer.current
            total   += layer.total
            if layer.is_extracted:
                extracted_bytes += layer.total
                extracted_count += 1
            if not layer.is_downloaded:
                is_all_downloaded = False

        layer_count = len(self.layers)

        # Nothing can be shown until Docker reports how big the layers are ..
        if total == 0:
            return

        rate = self.get_rate(now, current)

        if is_all_downloaded:
            rate = None

        # .. after which the download and the extraction each count for their share of the stage,
        # .. the extraction by the size of the layers extracted so far ..
        download_fraction = current / total
        extract_fraction = extracted_bytes / total
        fraction = download_fraction * _Download_Share + extract_fraction * (1 - _Download_Share)

        download = Download()
        download.current = current / _Bytes_Per_Unit
        download.total   = total / _Bytes_Per_Unit
        download.unit    = _Unit
        download.rate    = None if rate is None else rate / _Bytes_Per_Unit

        # .. and the layer being extracted shows how long it has taken so far.
        detail = self.get_extract_detail(extracted_count, layer_count)

        with self.progress.lock:
            self.stage.download = download
            self.stage.fraction = fraction
            self.stage.detail   = detail

# ################################################################################################################################
# ################################################################################################################################

def pull_image(progress:'Progress', image:'str') -> 'None':
    """ Pulls the image through the Docker Engine API, which reports the bytes of each layer as they arrive.
    """
    progress.advance_to(Stage_ID.Download)

    name, _, tag = image.partition(':')
    if not tag:
        tag = _Default_Tag

    query = urlencode({'fromImage': name, 'tag': tag})

    stage = progress.get_stage(Stage_ID.Download)
    tracker = PullTracker(progress, stage)
    connection = DockerConnection(_Read_Timeout)

    try:
        connection.request('POST', f'/images/create?{query}')
        response = connection.getresponse()

        # Docker rejects the pull outright if it cannot even start it ..
        if response.status != OK:
            body = response.read()
            data = json.loads(body)
            raise StageFailed(data['message'])

        # .. otherwise it sends one message per line until the image is in place.
        while line := response.readline():
            message = json.loads(line)
            tracker.handle(message)

    except OSError as exception:
        raise StageFailed(f'Image could not be downloaded: {exception}')

    finally:
        connection.close()

# ################################################################################################################################
# ################################################################################################################################
