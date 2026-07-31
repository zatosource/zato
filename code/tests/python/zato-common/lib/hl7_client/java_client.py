# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import stat
import subprocess
import zipfile
from urllib.request import urlretrieve

# Zato
from hl7_client.python_client import SendResult

# ################################################################################################################################
# ################################################################################################################################

# Where the Gradle project of the HAPI-based client lives
_Project_Directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'java', 'hl7-mllp-client'))

# What the application plugin installs and where - the launcher the runner invokes
_Install_Directory = os.path.join(_Project_Directory, 'build', 'install', 'hl7-mllp-client')
_Launcher_Path     = os.path.join(_Install_Directory, 'bin', 'hl7-mllp-client')

# The Gradle version the runner bootstraps when none is on PATH, and where it keeps it
_Gradle_Version         = '9.2.0'
_Gradle_Cache_Directory = os.path.abspath(os.path.join(_Project_Directory, '..', '.gradle-dist'))
_Gradle_Home            = os.path.join(_Gradle_Cache_Directory, f'gradle-{_Gradle_Version}')
_Gradle_Binary          = os.path.join(_Gradle_Home, 'bin', 'gradle')
_Gradle_Url             = f'https://services.gradle.org/distributions/gradle-{_Gradle_Version}-bin.zip'

# How long building is given - the first build downloads the HAPI dependencies too
_Build_Timeout = 600

# How long one send is given, above the client's own read timeout so that a listener that never
# answers is reported by the client rather than by the process being cut short here
_Send_Timeout = 60

# ################################################################################################################################
# ################################################################################################################################

def is_java_available() -> 'bool':
    """ Returns whether there is a Java runtime on this machine to build and run with.
    """
    out = bool(shutil.which('java'))
    return out

# ################################################################################################################################

def _bootstrap_gradle() -> 'str':
    """ Returns a Gradle binary to build with - the one on PATH when there is one, and otherwise
    the pinned distribution, downloaded from services.gradle.org once and reused ever after.
    """

    # A Gradle already installed on this machine is used as it is ..
    if gradle_on_path := shutil.which('gradle'):
        return gradle_on_path

    # .. and so is one this runner already bootstrapped ..
    if os.path.exists(_Gradle_Binary):
        return _Gradle_Binary

    # .. otherwise the pinned distribution is downloaded ..
    os.makedirs(_Gradle_Cache_Directory, exist_ok=True)
    archive_path = os.path.join(_Gradle_Cache_Directory, f'gradle-{_Gradle_Version}-bin.zip')

    print(f'[BUILD] Downloading Gradle {_Gradle_Version} from {_Gradle_Url}')
    _ = urlretrieve(_Gradle_Url, archive_path)

    # .. unpacked next to where it was downloaded to ..
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(_Gradle_Cache_Directory)

    # .. the launcher made runnable, which unzipping does not preserve ..
    launcher_mode = os.stat(_Gradle_Binary).st_mode
    os.chmod(_Gradle_Binary, launcher_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # .. and the archive itself is not needed any longer.
    os.remove(archive_path)

    return _Gradle_Binary

# ################################################################################################################################

def _newest_source_mtime() -> 'float':
    """ Returns the modification time of the most recently changed file among the project's
    build scripts and sources, which is what decides whether the installed client is current.
    """
    out = 0.0

    for directory_path, directory_names, file_names in os.walk(_Project_Directory):

        # What Gradle itself writes is not a source
        for gradle_output in ('build', '.gradle'):
            if gradle_output in directory_names:
                directory_names.remove(gradle_output)

        for file_name in file_names:
            file_path = os.path.join(directory_path, file_name)
            file_mtime = os.path.getmtime(file_path)

            if file_mtime > out:
                out = file_mtime

    return out

# ################################################################################################################################

def _needs_build() -> 'bool':
    """ Returns whether the client has to be built, which is the case for a tree that has never
    been built and for one whose sources have been edited since it last was.
    """
    if not os.path.exists(_Launcher_Path):
        return True

    launcher_mtime = os.path.getmtime(_Launcher_Path)
    source_mtime = _newest_source_mtime()

    out = source_mtime > launcher_mtime
    return out

# ################################################################################################################################

def build_client() -> 'None':
    """ Builds the HAPI client with Gradle, unless what is already installed is newer than
    its sources. The first build downloads the HAPI dependencies from Maven Central.
    """
    if not _needs_build():
        print('[BUILD] The Java HAPI client is up to date')
        return

    gradle_binary = _bootstrap_gradle()

    command = [gradle_binary, '--no-daemon', '-p', _Project_Directory, 'installDist']
    result = subprocess.run(command, capture_output=True, text=True, timeout=_Build_Timeout)

    if result.returncode != 0:
        raise Exception(f'Could not build the Java HAPI client:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    print(f'[BUILD] Built the Java HAPI client into {_Install_Directory}')

# ################################################################################################################################

def _parse_output(output:'str') -> 'SendResult':
    """ Reads the MSA fields out of the lines the client printed.
    """
    fields = {}

    for line in output.splitlines():
        if '=' in line:
            key, _, value = line.partition('=')
            fields[key] = value

    if 'msa_1' not in fields:
        raise Exception(f'No MSA fields in the Java client output:\n{output}')

    out = SendResult(fields['msa_1'], fields['msa_2'], fields['msa_3'])
    return out

# ################################################################################################################################

def send_message(
    host:'str',
    port:'int',
    control_id:'str',
    sending_app:'str',
    sending_facility:'str' = '',
    message_type:'str' = 'ADT',
    trigger_event:'str' = 'A01',
    ) -> 'SendResult':
    """ Sends one HL7 message with the Java HAPI client and returns what its acknowledgment's
    MSA segment said. The client is built first when it has to be.
    """
    build_client()

    command = [
        _Launcher_Path,
        '--host', host,
        '--port', str(port),
        '--control-id', control_id,
        '--sending-app', sending_app,
        '--sending-facility', sending_facility,
        '--message-type', message_type,
        '--trigger-event', trigger_event,
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_Send_Timeout)

    if result.returncode != 0:
        raise Exception(f'The Java HAPI client failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    out = _parse_output(result.stdout)
    return out

# ################################################################################################################################
# ################################################################################################################################
