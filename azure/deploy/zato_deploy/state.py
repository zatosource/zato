# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import time
from dataclasses import dataclass
from logging import getLogger
from threading import RLock

# Zato
from zato_deploy.common import anydict, anylist, floatnone, Line_Kind, Path, Stage_ID, Status, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Component:
    name:       str
    log_prefix: str
    check:      str
    status:     str

# ################################################################################################################################

@dataclass(init=False)
class Download:
    current: float
    total:   float
    unit:    str
    rate:    floatnone

# ################################################################################################################################

@dataclass(init=False)
class LogLine:
    id:   int
    time: float
    text: str
    kind: strnone

# ################################################################################################################################

component_list = list[Component]
log_line_list  = list[LogLine]
stage_list     = list['Stage']
strstagedict   = dict[str, 'Stage']

# ################################################################################################################################
# ################################################################################################################################

class Stage:
    """ One step of the deployment, as the page lists it.
    """
    def __init__(self, stage_id:'str', name:'str', weight:'int', source:'str') -> 'None':

        self.id     = stage_id
        self.name   = name
        self.weight = weight
        self.source = source
        self.status = Status.Pending

        self.started:    'floatnone'              = None
        self.finished:   'floatnone'              = None
        self.fraction:   'floatnone'              = None
        self.download:   'Download | None'        = None
        self.detail:     'strnone'                = None
        self.components: 'component_list | None'  = None

# ################################################################################################################################

    def to_dict(self) -> 'anydict':

        if self.download:
            download = {
                'current': self.download.current,
                'total':   self.download.total,
                'unit':    self.download.unit,
                'rate':    self.download.rate,
            }
        else:
            download = None

        components:'anylist | None' = None

        if self.components is not None:
            components = []
            for component in self.components:
                components.append({'name': component.name, 'status': component.status})

        out = {
            'id':         self.id,
            'name':       self.name,
            'weight':     self.weight,
            'status':     self.status,
            'started':    self.started,
            'finished':   self.finished,
            'fraction':   self.fraction,
            'progress':   download,
            'detail':     self.detail,
            'components': components,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

class Progress:
    """ Everything the page shows, shared by the stages that fill it in and the server that returns it.
    """
    def __init__(self, stages:'stage_list', ssh_command:'str') -> 'None':

        self.lock        = RLock()
        self.started     = time.time()
        self.stages      = stages
        self.ssh_command = ssh_command
        self.is_ready    = False

        self.lines:           'log_line_list' = []
        self.failure_stage:   'strnone'       = None
        self.failure_message: 'strnone'       = None

        self.stage_by_id:'strstagedict' = {}
        for stage in stages:
            self.stage_by_id[stage.id] = stage

# ################################################################################################################################

    def get_stage(self, stage_id:'str') -> 'Stage':
        out = self.stage_by_id[stage_id]
        return out

# ################################################################################################################################

    def get_current_stage(self) -> 'Stage':
        """ Returns the stage that runs or failed, or the last one once they all finished.
        """
        with self.lock:
            for stage in self.stages:
                if stage.status in (Status.Active, Status.Failed):
                    out = stage
                    break
            else:
                out = self.stages[-1]

        return out

# ################################################################################################################################

    def advance_to(self, stage_id:'str') -> 'None':
        """ Finishes every stage before the given one and starts it, unless it started already.
        """
        now = time.time()

        with self.lock:
            for stage in self.stages:

                # The stages before this one are finished ..
                if stage.id != stage_id:
                    if stage.status != Status.Done:
                        if stage.started is None:
                            stage.started = now
                        stage.status   = Status.Done
                        stage.finished = now
                    continue

                # .. and this one starts, unless it runs already.
                if stage.status == Status.Pending:
                    stage.status  = Status.Active
                    stage.started = now
                    self._write_serial_console(stage.name)
                break

# ################################################################################################################################

    def finish_all(self) -> 'None':
        """ Finishes every stage, which is what makes the environment ready.
        """
        now = time.time()

        with self.lock:
            for stage in self.stages:
                if stage.status != Status.Done:
                    if stage.started is None:
                        stage.started = now
                    stage.status   = Status.Done
                    stage.finished = now
            self.is_ready = True

        self._write_serial_console('The environment is ready')

# ################################################################################################################################

    def fail(self, message:'str', needs_log:'bool'=True) -> 'None':
        """ Marks the stage that runs now as failed, which ends the deployment.
        """
        now = time.time()

        with self.lock:

            # Only the first failure is the one to show ..
            if self.failure_message is not None:
                return

            stage = self.get_current_stage()

            if stage.started is None:
                stage.started = now

            stage.status   = Status.Failed
            stage.finished = now

            # .. of the components that were still starting, the first one is what failed, and the rest never finished ..
            if stage.components:
                has_failed_component = False
                for component in stage.components:
                    if component.status == Status.Active:
                        if has_failed_component:
                            component.status = Status.Pending
                        else:
                            component.status = Status.Failed
                            has_failed_component = True

            # .. and the reason goes both to the status and to the log, unless it came from the log.
            self.failure_stage   = stage.id
            self.failure_message = message

            if needs_log:
                self.log(message, Line_Kind.Error)

        self._write_serial_console(f'Deployment failed: {message}')

# ################################################################################################################################

    def has_failed(self) -> 'bool':
        with self.lock:
            out = self.failure_message is not None
        return out

# ################################################################################################################################

    def log(self, text:'str', kind:'strnone'=None) -> 'None':

        with self.lock:
            line_count = len(self.lines)

            line = LogLine()
            line.id   = line_count + 1
            line.time = time.time()
            line.text = text
            line.kind = kind

            self.lines.append(line)

        logger.info('%s', text)

# ################################################################################################################################

    def _write_serial_console(self, text:'str') -> 'None':
        """ Shows the progress in the boot diagnostics of the virtual machine too.
        """
        try:
            with open(Path.Serial_Console, 'w') as console:
                _ = console.write(f'Zato - {text}\n')
        except OSError:
            pass

# ################################################################################################################################

    def to_json(self, after:'int') -> 'bytes':
        """ Returns what the page reads on each poll, with only the log lines it has not seen yet.
        """
        with self.lock:

            stages:'anylist' = []
            for stage in self.stages:
                stage_dict = stage.to_dict()
                stages.append(stage_dict)

            lines:'anylist' = []
            for line in self.lines[after:]:
                lines.append({'id': line.id, 'time': line.time, 'text': line.text, 'kind': line.kind})

            if self.failure_message is None:
                failure = None
            else:
                failure = {'stage': self.failure_stage, 'message': self.failure_message}

            current_stage = self.get_current_stage()

            data = {
                'started':     self.started,
                'now':         time.time(),
                'is_ready':    self.is_ready,
                'failure':     failure,
                'ssh_command': self.ssh_command,
                'stages':      stages,
                'log': {
                    'source': current_stage.source,
                    'lines':  lines,
                },
            }

        out = json.dumps(data).encode('utf8')
        return out

# ################################################################################################################################
# ################################################################################################################################

def build_stages(image:'str') -> 'stage_list':
    """ Returns the stages in the order they run, each weighed by how many seconds it usually takes.
    """
    out = [
        Stage(Stage_ID.Certificate,  'Getting a Let\'s Encrypt certificate', 14,  'lego'),
        Stage(Stage_ID.Docker,       'Installing Docker',                    38,  'apt-get install docker.io'),
        Stage(Stage_ID.Storage,      'Preparing local storage',              9,   'zato-deploy'),
        Stage(Stage_ID.Download,     'Downloading Zato',                     150, f'docker pull {image}'),
        Stage(Stage_ID.Requirements, 'Installing requirements',              18,  'docker logs zato'),
        Stage(Stage_ID.Environment,  'Creating the environment',             26,  'docker logs zato'),
        Stage(Stage_ID.Components,   'Starting components',                  36,  'docker logs zato'),
        Stage(Stage_ID.Checking,     'Checking the environment',             8,   'zato-deploy'),
    ]

    return out

# ################################################################################################################################
# ################################################################################################################################
