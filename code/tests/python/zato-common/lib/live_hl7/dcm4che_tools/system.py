# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from shutil import copyfile
from tempfile import mkdtemp

# Live HL7
from live_hl7.dcm4che_tools.dicom import build_instance
from live_hl7.system import LiveSystem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strintdict, strlist, strstrdict
    from live_hl7.dcm4che_tools.dicom import Instance
    from live_hl7.system import Handle

# ################################################################################################################################
# ################################################################################################################################

# The service name in the compose file
Service = 'tools'

# Where the tools live in the image
_bin = '/opt/dcm4che/bin'

# The host directory mounted here is where files to send are placed
_work = '/work'

# The environment variable naming the host directory the compose file mounts
Work_Dir_Env = 'DCM4CHE_TOOLS_WORK_DIR'

# ################################################################################################################################
# ################################################################################################################################

class DCM4CHETools(LiveSystem):
    """ The dcm4che command line tools - a modality that stores images and a foreign HL7 sender,
    each run inside the container on demand.
    """

    name = 'dcm4che_tools'
    block_number = 8
    purposes = ()
    images = {'tools': 'dcm4che/dcm4che-tools:5.33.1'}
    directory = os.path.dirname(__file__)
    summary = 'The dcm4che tools - storescu, findscu and hl7snd run on demand, no ports of their own.'

# ################################################################################################################################

    def environment(self, ports:'strintdict', password:'str') -> 'strstrdict':
        out = super().environment(ports, password)
        out[Work_Dir_Env] = mkdtemp(prefix='zato-hl7-dcm4che-tools-')

        return out

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        out = handle.stack.is_running(Service)
        return out

# ################################################################################################################################
# ################################################################################################################################

def work_dir(handle:'Handle') -> 'str':
    out = handle.stack.environment[Work_Dir_Env]
    return out

# ################################################################################################################################

def _place(handle:'Handle', path:'str') -> 'str':
    """ Copies a host file into the work directory unless it is there already, returning the container path.
    """
    directory = work_dir(handle)
    name = os.path.basename(path)
    target = os.path.join(directory, name)

    if os.path.abspath(path) != os.path.abspath(target):
        _ = copyfile(path, target)

    out = f'{_work}/{name}'
    return out

# ################################################################################################################################

def _tool(handle:'Handle', tool:'str', arguments:'strlist') -> 'str':
    command = [f'{_bin}/{tool}']
    command.extend(arguments)

    out = handle.stack.exec(Service, command)
    return out

# ################################################################################################################################

def storescu(handle:'Handle', host:'str', port:'int', aet:'str', dicom_path:'str') -> 'str':
    """ Sends one DICOM file to an archive with C-STORE and returns the tool's output.
    """
    container_path = _place(handle, dicom_path)

    out = _tool(handle, 'storescu', ['-c', f'{aet}@{host}:{port}', container_path])
    return out

# ################################################################################################################################

def findscu(handle:'Handle', host:'str', port:'int', aet:'str', arguments:'strlist') -> 'str':
    """ Runs a C-FIND with the arguments given, e.g. -M MWL -m AccessionNumber=A1, and returns the tool's output.
    """
    command = ['-c', f'{aet}@{host}:{port}']
    command.extend(arguments)

    out = _tool(handle, 'findscu', command)
    return out

# ################################################################################################################################

def hl7snd(handle:'Handle', host:'str', port:'int', message:'bytes') -> 'str':
    """ Sends one HL7 message over MLLP and returns the tool's output, the acknowledgement included.
    """
    directory = work_dir(handle)
    path = os.path.join(directory, 'message.hl7')

    with open(path, 'wb') as message_file:
        _ = message_file.write(message)

    out = _tool(handle, 'hl7snd', ['-c', f'{host}:{port}', f'{_work}/message.hl7'])
    return out

# ################################################################################################################################

def new_instance(handle:'Handle', *, patient_id:'str', patient_name:'str', accession:'str') -> 'Instance':
    """ Builds a CT instance in the work directory, ready for storescu.
    """
    directory = work_dir(handle)

    out = build_instance(directory, patient_id=patient_id, patient_name=patient_name, accession=accession)
    return out

# ################################################################################################################################
# ################################################################################################################################
