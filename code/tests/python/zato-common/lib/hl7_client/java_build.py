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

# ################################################################################################################################
# ################################################################################################################################

# Where the Gradle projects the tests build live, one directory per project
_Java_Directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'java'))

# The Gradle version the runner bootstraps when none is on PATH, and where it keeps it
_Gradle_Version         = '9.2.0'
_Gradle_Cache_Directory = os.path.join(_Java_Directory, '.gradle-dist')
_Gradle_Home            = os.path.join(_Gradle_Cache_Directory, f'gradle-{_Gradle_Version}')
_Gradle_Binary          = os.path.join(_Gradle_Home, 'bin', 'gradle')
_Gradle_Url             = f'https://services.gradle.org/distributions/gradle-{_Gradle_Version}-bin.zip'

# How long building is given - the first build downloads the HAPI dependencies too
_Build_Timeout = 600

# ################################################################################################################################
# ################################################################################################################################

def is_java_available() -> 'bool':
    """ Returns whether there is a Java runtime on this machine to build and run with.
    """
    out = bool(shutil.which('java'))
    return out

# ################################################################################################################################

def get_project_directory(project_name:'str') -> 'str':
    """ Returns where one of the Gradle projects the tests build lives.
    """
    out = os.path.join(_Java_Directory, project_name)
    return out

# ################################################################################################################################

def get_launcher_path(project_name:'str') -> 'str':
    """ Returns the launcher the application plugin installs for one project, which is what a
    test runs rather than invoking Java itself.
    """
    project_directory = get_project_directory(project_name)

    out = os.path.join(project_directory, 'build', 'install', project_name, 'bin', project_name)
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

def _newest_source_mtime(project_directory:'str') -> 'float':
    """ Returns the modification time of the most recently changed file among one project's build
    scripts and sources, which is what decides whether what is installed is current.
    """
    out = 0.0

    for directory_path, directory_names, file_names in os.walk(project_directory):

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

def _needs_build(project_directory:'str', launcher_path:'str') -> 'bool':
    """ Returns whether a project has to be built, which is the case for a tree that has never
    been built and for one whose sources have been edited since it last was.
    """
    if not os.path.exists(launcher_path):
        return True

    launcher_mtime = os.path.getmtime(launcher_path)
    source_mtime = _newest_source_mtime(project_directory)

    out = source_mtime > launcher_mtime
    return out

# ################################################################################################################################

def build_project(project_name:'str') -> 'str':
    """ Builds one Gradle project with Gradle unless what is already installed is newer than its
    sources, and returns the launcher to run it by. The first build of either project downloads
    the HAPI dependencies from Maven Central.
    """
    project_directory = get_project_directory(project_name)
    launcher_path = get_launcher_path(project_name)

    if not _needs_build(project_directory, launcher_path):
        print(f'[BUILD] {project_name} is up to date')
        return launcher_path

    gradle_binary = _bootstrap_gradle()

    command = [gradle_binary, '--no-daemon', '-p', project_directory, 'installDist']
    result = subprocess.run(command, capture_output=True, text=True, timeout=_Build_Timeout)

    if result.returncode != 0:
        raise Exception(f'Could not build {project_name}:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    print(f'[BUILD] Built {project_name} into {os.path.dirname(launcher_path)}')

    return launcher_path

# ################################################################################################################################
# ################################################################################################################################
