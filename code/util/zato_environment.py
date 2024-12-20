# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import glob
import logging
import os
import platform
import sys
from pathlib import Path
from subprocess import check_output, PIPE, Popen
from sys import version as py_version

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist, strnone # type: ignore

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

platform_system = platform.system().lower()

is_windows = 'windows' in platform_system
is_linux   = 'linux'   in platform_system # noqa: E272

# ################################################################################################################################
# ################################################################################################################################

if '3.8' in py_version:
    setuptools_version = '57.4.0'
else:
    setuptools_version = '75.6.0'

pip_deps_windows     = f'setuptools=={setuptools_version} wheel'
pip_deps_non_windows = f'setuptools=={setuptools_version} wheel pip'
pip_deps = pip_deps_windows if is_windows else pip_deps_non_windows

# ################################################################################################################################
# ################################################################################################################################

zato_command_template_linux = r"""
#!{bin_dir}/python

# To prevent an attribute error in pyreadline\py3k_compat.py
# AttributeError: module 'collections' has no attribute 'Callable'

try:
    import collections
    collections.Callable = collections.abc.Callable
except AttributeError:
    pass

# Zato
from zato.cli.zato_command import main

if __name__ == '__main__':

    # stdlib
    import re
    import sys

    # This is needed by SUSE
    sys.path.append(r'{base_dir}/lib64/python3.6/site-packages/')

    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
""".strip() # noqa: W605

zato_command_template_windows = r"""
@echo off
"{bundled_python_dir}\python.exe" "\\?\{code_dir}\\zato-cli\\src\\zato\\cli\\_run_zato.py" %*
""".strip() # noqa: W605

# ################################################################################################################################
# ################################################################################################################################

class EnvironmentManager:

    def __init__(self, base_dir:'str', bin_dir:'str') -> 'None':
        self.base_dir = base_dir
        self.bin_dir = bin_dir
        self.pip_options = ''
        self.eggs_dir = 'invalid-self.eggs_dir'
        self.bundle_ext_dir = 'invalid-bundle_ext_dir'
        self.site_packages_dir = 'invalid-site_packages_dir'
        self.pip_pyz_path = 'invalid-pip_pyz_path'
        self.python_command = 'invalid-python_command'
        self.pip_command = 'invalid-pip_command'
        self.bundled_python_dir = 'invalid-bundled_python_dir'
        self.zato_reqs_path = 'invalid-zato_reqs_path'
        self.code_dir = 'invalid-code_dir'

        self._set_up_pip_flags()
        self._set_up_dir_and_attr_names()

# ################################################################################################################################

    def _get_linux_distro_name(self) -> 'str':

        # Short-cut for non-Linux systems
        if not is_linux:
            return ''

        # If we are here, it means that we are under a Linux distribution and we assume
        # that the file exists per https://www.freedesktop.org/software/systemd/man/os-release.html

        # By default, we do not have it
        distro_name = ''

        data = open('/etc/os-release').read()
        data = data.splitlines()

        for line in data:
            if line.startswith('PRETTY_NAME'):

                line = line.split('=')

                distro_name = line[1]
                distro_name = distro_name.replace('"', '')
                distro_name = distro_name.lower()

                break

        logger.info('Linux distribution found -> `%s`', distro_name)
        return distro_name

# ################################################################################################################################

    def _set_up_pip_flags(self) -> 'None':

        #
        # Under RHEL, pip install may not have the '--no-warn-script-location' flag.
        # At the same time, under RHEL, we need to use --no-cache-dir.
        #

        linux_distro = self._get_linux_distro_name()
        is_rhel = 'red hat' in linux_distro or 'centos' in linux_distro

        # Explicitly ignore the non-existing option and add a different one..
        if is_rhel:
            self.pip_options = '--no-cache-dir'

        # .. or make use of it.
        else:
            self.pip_options = '--no-warn-script-location'

# ################################################################################################################################

    def _set_up_dir_and_attr_names(self) -> 'None':

        # This needs to be checked in runtime because we do not know
        # under what Python version we are are going to run.
        py_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
        logger.info('Python version maj.min -> %s', py_version)
        logger.info('Python self.base_dir -> %s', self.base_dir)

        self.bundle_ext_dir = os.path.join(self.base_dir, '..')
        self.bundle_ext_dir = os.path.abspath(self.bundle_ext_dir)
        logger.info('Bundle ext. dir -> %s', self.bundle_ext_dir)

        # This will exist only under Windows
        if is_windows:

            # Dynamically check what our current embedded Python's directory is ..
            self.bundled_python_dir = self.get_bundled_python_version(self.bundle_ext_dir, 'windows')

        # Under Linux, the path to site-packages contains the Python version but it does not under Windows.
        # E.g. ~/src-zato/lib/python3.8/site-packages vs. C:\src-zato\lib\site-packages
        if is_linux:
            python_version_dir = 'python' + py_version
            py_lib_dir = os.path.join('lib', python_version_dir)
        else:
            py_lib_dir = os.path.join(self.bundled_python_dir, 'lib')

        py_lib_dir = os.path.abspath(py_lib_dir)
        logger.info('Python lib dir -> %s', py_lib_dir)

        self.site_packages_dir = os.path.join(py_lib_dir, 'site-packages')
        self.site_packages_dir = os.path.abspath(self.site_packages_dir)
        logger.info('Python site-packages dir -> %s', self.site_packages_dir)

        self.eggs_dir = os.path.join(self.base_dir, 'eggs')
        self.eggs_dir = os.path.abspath(self.eggs_dir)
        logger.info('Python eggs dir -> %s', self.eggs_dir)

        if is_windows:

            # This is always in the same location
            self.pip_pyz_path = os.path.join(self.bundle_ext_dir, 'pip', 'pip.pyz')

            # .. and build the full Python command now.
            self.python_command = os.path.join(self.bundled_python_dir, 'python.exe')

            # We are now ready to build the full pip command ..
            self.pip_command = f'{self.python_command} {self.pip_pyz_path}'

            # .. and the install prefix as well.
            self.pip_install_prefix = f'--prefix {self.bundled_python_dir}'

            # Where we keep our own requirements
            self.zato_reqs_path = os.path.join(self.base_dir, '..', '..', 'requirements.txt')
            self.zato_reqs_path = os.path.abspath(self.zato_reqs_path)

            # Where the zato-* packages are (the "code" directory)
            self.code_dir = os.path.join(self.bundle_ext_dir, '..')
            self.code_dir = os.path.abspath(self.code_dir)

        else:

            # These are always in the same location
            self.pip_command = os.path.join(self.bin_dir, 'pip')
            self.python_command = os.path.join(self.bin_dir, 'python')
            self.code_dir = self.base_dir
            self.zato_reqs_path = os.path.join(self.base_dir, 'requirements.txt')

            # This is not used under Linux
            self.pip_install_prefix = ''

# ################################################################################################################################

    def get_bundled_python_version(self, bundle_ext_dir:'str', os_type:'str') -> 'str':

        python_parent_dir = f'python-{os_type}'
        python_parent_dir = os.path.join(bundle_ext_dir, python_parent_dir)

        # We want to ignore any names other than ones matching this pattern
        pattern = os.path.join(python_parent_dir, 'python-*')

        results = []

        for item in glob.glob(pattern):
            results.append(item)

        if not results:
            raise Exception(f'No bundled Python version found matching pattern: `{pattern}`')

        if len(results) > 1:
            raise Exception(f'Too many results found matching pattern: `{pattern}` -> `{results}`')

        # If we are here, it means that we have exactly one result that we can return to our caller
        result = results[0]
        return result

# ################################################################################################################################

    def _create_symlink(self, from_:'str', to:'str') -> 'None':

        try:
            os.symlink(from_, to)
        except FileExistsError:
            # It is not an issue if it exists, likely install.sh/.bat ran twice.
            pass
        else:
            logger.info('Symlinked from  `%s` to `%s`', from_, to)

# ################################################################################################################################

    def _create_executable(self, path:'str', data:'str') -> 'None':

        f = open(path, 'w')
        _ = f.write(data)
        f.close()

        logger.info('Created file `%s`', path)

        # .. and make it executable.
        os.chmod(path, 0o740)

        logger.info('Made file executable `%s`', path)

# ################################################################################################################################

    def run_command(
        self,
        command:'str',
        exit_on_error:'bool'=True,
        needs_stdout:'bool'=False,
        needs_stderr:'bool'=False,
        log_stderr:'bool'=True,
        use_check_output:'bool'=False
    ) -> 'str | None':

        logger.info('Running `%s`', command)

        # Turn what is possibly a multi-line command into a list of arguments ..
        command = command.strip()
        command_split = command.split()

        func = self._run_check_output if use_check_output else self._run_popen
        return func(command_split, exit_on_error, needs_stdout, needs_stderr, log_stderr)

# ################################################################################################################################

    def _run_check_output(
        self,
        command:'strlist',
        exit_on_error:'bool'=True,
        needs_stdout:'bool'=False,
        needs_stderr:'bool'=False,
        log_stderr:'bool'=True
    ) -> 'any_':

        # This will be potentially returned to our caller
        stdout = b''

        # Run the command ..
        try:
            stdout = check_output(command) # type: bytes
        except Exception as e:
            stderr = e.args
            if log_stderr:
                logger.warning(stderr)
            if exit_on_error:
                sys.exit(1)
            else:
                if needs_stderr:
                    return stderr
        else:
            if needs_stdout:
                return stdout.decode('utf8')

# ################################################################################################################################

    def _run_popen(
        self,
        command:'str | strlist',
        exit_on_error:'bool'=True,
        needs_stdout:'bool'=False,
        needs_stderr:'bool'=False,
        log_stderr:'bool'=True
    ) -> 'strnone':

        # This will be potentially returned to our caller
        stdout = None

        # Run the command ..
        process = Popen(command, stderr=PIPE, stdout=PIPE if needs_stdout else None)

        # .. and wait until it completes.
        while True:

            stderr = process.stderr.readline() # type: ignore

            if needs_stdout:
                stdout = process.stdout.readline() # type: ignore
                stdout = stdout.strip()
                stdout = stdout.decode('utf8')

            if stderr:
                stderr = stderr.strip()
                stderr = stderr.decode('utf8')

                if log_stderr:
                    logger.warning(stderr)

                if exit_on_error:
                    process.kill()
                    sys.exit(1)
                else:
                    if needs_stderr:
                        return stderr

            if process.poll() is not None:
                break

        if needs_stdout:
            return stdout

# ################################################################################################################################

    def pip_install_core_pip(self) -> 'None':

        # Set up the command ..
        command = '{pip_command} install {pip_install_prefix} {pip_options} -U {pip_deps}'.format(**{
            'pip_command': self.pip_command,
            'pip_install_prefix': self.pip_install_prefix,
            'pip_options': self.pip_options,
            'pip_deps':    pip_deps,
        })

        # .. and run it.
        _ = self.run_command(command, exit_on_error=True)

# ################################################################################################################################

    def pip_install_requirements_by_path(self, reqs_path:'str', exit_on_error:'bool'=False) -> 'None':

        if not os.path.exists(reqs_path):
            logger.info('Skipped user-defined requirements.txt. No such path `%s`.', reqs_path)
            return

        # Set up the command ..
        command = """
            {pip_command}
            -v
            install
            {pip_install_prefix}
            {pip_options}
            -r {reqs_path}
        """.format(**{
               'pip_command': self.pip_command,
               'pip_install_prefix': self.pip_install_prefix,
               'pip_options': self.pip_options,
               'reqs_path':   reqs_path
            })

        # .. and run it.
        _ = self.run_command(command, exit_on_error=exit_on_error)

# ################################################################################################################################

    def pip_install_zato_requirements(self) -> 'None':

        # Install our own requirements
        self.pip_install_requirements_by_path(self.zato_reqs_path, exit_on_error=False)

# ################################################################################################################################

    def run_pip_install_zato_packages(self, packages:'strlist', allow_editable:'bool'=True) -> 'None':

        # All the -e arguments that pip will receive
        pip_args = []

        # This is used everywhere except with Cython
        if allow_editable:
            pip_args.append('--use-pep517')

        # Build the arguments
        for name in packages:
            package_path = os.path.join(self.code_dir, name)
            arg = '-e {}'.format(package_path)
            pip_args.append(arg)

        # Build the command ..
        command = '{pip_command} install {pip_install_prefix} --no-warn-script-location {pip_args}'.format(**{
            'pip_command': self.pip_command,
            'pip_install_prefix': self.pip_install_prefix,
            'pip_args': ' '.join(pip_args)
        })

        # .. and run it.
        _ = self.run_command(command, exit_on_error=False)

# ################################################################################################################################

    def pip_install_standalone_requirements(self) -> 'None':

        # These cannot be installed via requirements.txt
        packages = [
            'cython==3.1.0a1',
            'pyOpenSSL==23.0.0',
            'zato-ext-bunch==1.2',
        ]

        # This needs to be installed here rather than via requirements.txt
        if not is_windows:
            packages.append('posix-ipc==1.0.0')

        for package in packages:

            # Set up the command ..
            command = '{pip_command} install {pip_install_prefix} --no-warn-script-location {package}'.format(**{
                'pip_command': self.pip_command,
                'pip_install_prefix': self.pip_install_prefix,
                'package': package,
            })

            # .. and run it.
            _ = self.run_command(command, exit_on_error=True)

# ################################################################################################################################

    def pip_install_zato_packages(self) -> 'None':

        # Note that zato-common must come first.
        editable_packages = [
            'zato-common',
            'zato-agent',
            'zato-broker',
            'zato-cli',
            'zato-client',
            'zato-distlock',
            'zato-hl7',
            'zato-lib',
            'zato-scheduler',
            'zato-server',
            'zato-web-admin',
            'zato-zmq',
            'zato-sso',
            'zato-testing',
        ]

        non_editable_packages = [
            'zato-cy'
        ]

        self.run_pip_install_zato_packages(editable_packages)
        self.run_pip_install_zato_packages(non_editable_packages, allow_editable=False)

# ################################################################################################################################

    def pip_uninstall(self) -> 'None':

        # Packages that will be uninstalled, e.g. no longer needed
        packages = [
            'imbox',
            'pycrypto',
            'python-keyczar',
        ]

        # Build the command ..
        command = '{} uninstall -y -qq {}'.format(self.pip_command, ' '.join(packages))

        # .. and run it.
        _ = self.run_command(command, exit_on_error=False)

# ################################################################################################################################

    def pip_install(self) -> 'None':
        self.pip_install_core_pip()
        self.pip_install_standalone_requirements()
        self.pip_install_zato_requirements()
        self.pip_install_zato_packages()
        self.pip_uninstall()

# ################################################################################################################################

    def update_git_revision(self) -> 'None':

        # This is where we will store our last git commit ID
        revision_file_path = os.path.join(self.base_dir, 'release-info', 'revision.txt')

        # Make sure the underlying git command runs in our git repository ..
        os.chdir(self.base_dir)

        # Build the command ..
        command = 'git log -n 1 --pretty=format:%H --no-color'

        # .. run the command to get our latest commit ID ..
        commit_id = self.run_command(command, needs_stdout=True, use_check_output=True)

        # .. and store it in an external file for 'zato --version' and other tools to use.
        f = open(revision_file_path, 'w')
        f.write(commit_id) # type: ignore
        f.close()

        logger.info('Git commit ID -> `%s`', commit_id)

# ################################################################################################################################

    def add_eggs_symlink(self) -> 'None':

        if not is_windows:
            self._create_symlink(self.site_packages_dir, self.eggs_dir)

# ################################################################################################################################

    def add_extlib_to_sys_path(self, extlib_dir:'Path') -> 'None':

        # This file contains entries that, in runtime, will be found in sys.path
        easy_install_path = os.path.join(self.site_packages_dir, 'easy-install.pth')

        # .. add the path to easy_install ..
        f = open(easy_install_path, 'a')
        _ = f.write(extlib_dir.as_posix())
        _ = f.write(os.linesep)
        f.close()

# ################################################################################################################################

    def add_extlib(self) -> 'None':

        # This is where external depdendencies can be kept
        extlib_dir_path = os.path.join(self.base_dir, 'extlib')

        # For backward compatibility, this will point to extlib
        extra_paths_dir = os.path.join(self.base_dir, 'zato_extra_paths')

        # Build a Path object ..
        extlib_dir = Path(extlib_dir_path)

        # .. create the underlying directory ..
        extlib_dir.mkdir(exist_ok=True)

        # .. add the path to easy_install ..
        self.add_extlib_to_sys_path(extlib_dir)

        # .. and symlink it for backward compatibility.
        if not is_windows:
            self._create_symlink(extlib_dir_path, extra_paths_dir)

# ################################################################################################################################

    def add_py_command(self) -> 'None':

        # This is where will will save it
        command_name = 'py.bat' if is_windows else 'py'
        py_command_path = os.path.join(self.bin_dir, command_name)

        # There will be two versions, one for Windows and one for other systems

        #
        # Windows
        #
        if is_windows:
            template = ''
            template += '"{}" %*'

        # Non-Windows
        else:
            template = ''
            template += '#!/bin/sh'
            template += '\n'
            template += '"{}" "$@"'

        # Add the full path to the OS-specific template ..
        data = template.format(self.python_command)

        # .. and add the file to the system.
        self._create_executable(py_command_path, data)

# ################################################################################################################################

    def add_zato_command(self) -> 'None':

        # Differentiate between Windows and other systems as the extension is needed under the former
        command_name = 'zato.bat' if is_windows else 'zato'

        if is_windows:
            command_name    = 'zato.bat'
            template        = zato_command_template_windows
            template_kwargs = {
                'code_dir': self.code_dir,
                'bundled_python_dir': self.bundled_python_dir,
            }
        else:
            command_name    = 'zato'
            template        = zato_command_template_linux
            template_kwargs = {
                'base_dir': self.base_dir,
                'bin_dir': self.bin_dir,
            }

        # This is where the command file will be created
        command_path = os.path.join(self.bin_dir, command_name)

        # Build the full contents of the command file ..
        data = template.format(**template_kwargs)

        # .. and add the file to the file system.
        self._create_executable(command_path, data)

# ################################################################################################################################

    def copy_patches(self) -> 'None':

        # Where our patches can be found
        patches_dir = os.path.join(self.code_dir, 'patches')

        # Where to copy them to
        dest_dir = self.site_packages_dir

        logger.info('Copying patches from %s -> %s', patches_dir, dest_dir)

        # Recursively copy all the patches, overwriting any files found
        _ = copy_tree(patches_dir, dest_dir, preserve_symlinks=True, verbose=1)

        logger.info('Copied patches from %s -> %s', patches_dir, dest_dir)

# ################################################################################################################################

    def install(self) -> 'None':

        # self.update_git_revision()
        self.pip_install()

        self.add_eggs_symlink()
        self.add_extlib()
        self.add_py_command()
        self.add_zato_command()
        self.copy_patches()

# ################################################################################################################################

    def update(self) -> 'None':

        self.update_git_revision()
        self.pip_install()
        self.copy_patches()

# ################################################################################################################################

    def runtime_setup_with_env_variables(self) -> 'None':

        # In this step, we need to look up any possible custom pip requirements
        # that we already know that are defined through environment variables.
        python_reqs = os.environ.get('ZATO_PYTHON_REQS', '')

        # OK, we have some requirements files to install packages from ..
        if python_reqs:

            # .. support multiple files on input ..
            python_reqs = python_reqs.split(':')

            # .. and install them now.
            for path in python_reqs:
                self.pip_install_requirements_by_path(path)

        # This step is similar but instead of installing dependencies from pip requirements,
        # we add to sys.path entire directories where runtime user code can be found.
        extlib_dir = os.environ.get('ZATO_EXTLIB_DIR', '')

        # OK, we have some requirements files to install packages from ..
        if extlib_dir:

            # .. support multiple files on input ..
            extlib_dir = extlib_dir.split(':')

            # .. and install them now.
            for path in extlib_dir:
                self.add_extlib_to_sys_path(Path(path))

# ################################################################################################################################
# ################################################################################################################################

# The code below is copied from Python 3.10 under the Python Software License.

"""
A. HISTORY OF THE SOFTWARE
==========================

Python was created in the early 1990s by Guido van Rossum at Stichting
Mathematisch Centrum (CWI, see https://www.cwi.nl) in the Netherlands
as a successor of a language called ABC.  Guido remains Python's
principal author, although it includes many contributions from others.

In 1995, Guido continued his work on Python at the Corporation for
National Research Initiatives (CNRI, see https://www.cnri.reston.va.us)
in Reston, Virginia where he released several versions of the
software.

In May 2000, Guido and the Python core development team moved to
BeOpen.com to form the BeOpen PythonLabs team.  In October of the same
year, the PythonLabs team moved to Digital Creations, which became
Zope Corporation.  In 2001, the Python Software Foundation (PSF, see
https://www.python.org/psf/) was formed, a non-profit organization
created specifically to own Python-related Intellectual Property.
Zope Corporation was a sponsoring member of the PSF.

All Python releases are Open Source (see https://opensource.org for
the Open Source Definition).  Historically, most, but not all, Python
releases have also been GPL-compatible; the table below summarizes
the various releases.

    Release         Derived     Year        Owner       GPL-
                    from                                compatible? (1)

    0.9.0 thru 1.2              1991-1995   CWI         yes
    1.3 thru 1.5.2  1.2         1995-1999   CNRI        yes
    1.6             1.5.2       2000        CNRI        no
    2.0             1.6         2000        BeOpen.com  no
    1.6.1           1.6         2001        CNRI        yes (2)
    2.1             2.0+1.6.1   2001        PSF         no
    2.0.1           2.0+1.6.1   2001        PSF         yes
    2.1.1           2.1+2.0.1   2001        PSF         yes
    2.1.2           2.1.1       2002        PSF         yes
    2.1.3           2.1.2       2002        PSF         yes
    2.2 and above   2.1.1       2001-now    PSF         yes

Footnotes:

(1) GPL-compatible doesn't mean that we're distributing Python under
    the GPL.  All Python licenses, unlike the GPL, let you distribute
    a modified version without making your changes open source.  The
    GPL-compatible licenses make it possible to combine Python with
    other software that is released under the GPL; the others don't.

(2) According to Richard Stallman, 1.6.1 is not GPL-compatible,
    because its license has a choice of law clause.  According to
    CNRI, however, Stallman's lawyer has told CNRI's lawyer that 1.6.1
    is "not incompatible" with the GPL.

Thanks to the many outside volunteers who have worked under Guido's
direction to make these releases possible.


B. TERMS AND CONDITIONS FOR ACCESSING OR OTHERWISE USING PYTHON
===============================================================

Python software and documentation are licensed under the
Python Software Foundation License Version 2.

Starting with Python 3.8.6, examples, recipes, and other code in
the documentation are dual licensed under the PSF License Version 2
and the Zero-Clause BSD license.

Some software incorporated into Python is under different licenses.
The licenses are listed with code falling under that license.


PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
--------------------------------------------

1. This LICENSE AGREEMENT is between the Python Software Foundation
("PSF"), and the Individual or Organization ("Licensee") accessing and
otherwise using this software ("Python") in source or binary form and
its associated documentation.

2. Subject to the terms and conditions of this License Agreement, PSF hereby
grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
analyze, test, perform and/or display publicly, prepare derivative works,
distribute, and otherwise use Python alone or in any derivative version,
provided, however, that PSF's License Agreement and PSF's notice of copyright,
i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010,
2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 Python Software Foundation;
All Rights Reserved" are retained in Python alone or in any derivative version
prepared by Licensee.

3. In the event Licensee prepares a derivative work that is based on
or incorporates Python or any part thereof, and wants to make
the derivative work available to others as provided herein, then
Licensee hereby agrees to include in any such work a brief summary of
the changes made to Python.

4. PSF is making Python available to Licensee on an "AS IS"
basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT
INFRINGE ANY THIRD PARTY RIGHTS.

5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON,
OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

7. Nothing in this License Agreement shall be deemed to create any
relationship of agency, partnership, or joint venture between PSF and
Licensee.  This License Agreement does not grant permission to use PSF
trademarks or trade name in a trademark sense to endorse or promote
products or services of Licensee, or any third party.

8. By copying, installing or otherwise using Python, Licensee
agrees to be bound by the terms and conditions of this License
Agreement.


BEOPEN.COM LICENSE AGREEMENT FOR PYTHON 2.0
-------------------------------------------

BEOPEN PYTHON OPEN SOURCE LICENSE AGREEMENT VERSION 1

1. This LICENSE AGREEMENT is between BeOpen.com ("BeOpen"), having an
office at 160 Saratoga Avenue, Santa Clara, CA 95051, and the
Individual or Organization ("Licensee") accessing and otherwise using
this software in source or binary form and its associated
documentation ("the Software").

2. Subject to the terms and conditions of this BeOpen Python License
Agreement, BeOpen hereby grants Licensee a non-exclusive,
royalty-free, world-wide license to reproduce, analyze, test, perform
and/or display publicly, prepare derivative works, distribute, and
otherwise use the Software alone or in any derivative version,
provided, however, that the BeOpen Python License is retained in the
Software, alone or in any derivative version prepared by Licensee.

3. BeOpen is making the Software available to Licensee on an "AS IS"
basis.  BEOPEN MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, BEOPEN MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE SOFTWARE WILL NOT
INFRINGE ANY THIRD PARTY RIGHTS.

4. BEOPEN SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF THE
SOFTWARE FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS
AS A RESULT OF USING, MODIFYING OR DISTRIBUTING THE SOFTWARE, OR ANY
DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

5. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

6. This License Agreement shall be governed by and interpreted in all
respects by the law of the State of California, excluding conflict of
law provisions.  Nothing in this License Agreement shall be deemed to
create any relationship of agency, partnership, or joint venture
between BeOpen and Licensee.  This License Agreement does not grant
permission to use BeOpen trademarks or trade names in a trademark
sense to endorse or promote products or services of Licensee, or any
third party.  As an exception, the "BeOpen Python" logos available at
http://www.pythonlabs.com/logos.html may be used according to the
permissions granted on that web page.

7. By copying, installing or otherwise using the software, Licensee
agrees to be bound by the terms and conditions of this License
Agreement.


CNRI LICENSE AGREEMENT FOR PYTHON 1.6.1
---------------------------------------

1. This LICENSE AGREEMENT is between the Corporation for National
Research Initiatives, having an office at 1895 Preston White Drive,
Reston, VA 20191 ("CNRI"), and the Individual or Organization
("Licensee") accessing and otherwise using Python 1.6.1 software in
source or binary form and its associated documentation.

2. Subject to the terms and conditions of this License Agreement, CNRI
hereby grants Licensee a nonexclusive, royalty-free, world-wide
license to reproduce, analyze, test, perform and/or display publicly,
prepare derivative works, distribute, and otherwise use Python 1.6.1
alone or in any derivative version, provided, however, that CNRI's
License Agreement and CNRI's notice of copyright, i.e., "Copyright (c)
1995-2001 Corporation for National Research Initiatives; All Rights
Reserved" are retained in Python 1.6.1 alone or in any derivative
version prepared by Licensee.  Alternately, in lieu of CNRI's License
Agreement, Licensee may substitute the following text (omitting the
quotes): "Python 1.6.1 is made available subject to the terms and
conditions in CNRI's License Agreement.  This Agreement together with
Python 1.6.1 may be located on the internet using the following
unique, persistent identifier (known as a handle): 1895.22/1013.  This
Agreement may also be obtained from a proxy server on the internet
using the following URL: http://hdl.handle.net/1895.22/1013".

3. In the event Licensee prepares a derivative work that is based on
or incorporates Python 1.6.1 or any part thereof, and wants to make
the derivative work available to others as provided herein, then
Licensee hereby agrees to include in any such work a brief summary of
the changes made to Python 1.6.1.

4. CNRI is making Python 1.6.1 available to Licensee on an "AS IS"
basis.  CNRI MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR
IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, CNRI MAKES NO AND
DISCLAIMS ANY REPRESENTATION OR WARRANTY OF MERCHANTABILITY OR FITNESS
FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON 1.6.1 WILL NOT
INFRINGE ANY THIRD PARTY RIGHTS.

5. CNRI SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON
1.6.1 FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES OR LOSS AS
A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON 1.6.1,
OR ANY DERIVATIVE THEREOF, EVEN IF ADVISED OF THE POSSIBILITY THEREOF.

6. This License Agreement will automatically terminate upon a material
breach of its terms and conditions.

7. This License Agreement shall be governed by the federal
intellectual property law of the United States, including without
limitation the federal copyright law, and, to the extent such
U.S. federal law does not apply, by the law of the Commonwealth of
Virginia, excluding Virginia's conflict of law provisions.
Notwithstanding the foregoing, with regard to derivative works based
on Python 1.6.1 that incorporate non-separable material that was
previously distributed under the GNU General Public License (GPL), the
law of the Commonwealth of Virginia shall govern this License
Agreement only as to issues arising under or with respect to
Paragraphs 4, 5, and 7 of this License Agreement.  Nothing in this
License Agreement shall be deemed to create any relationship of
agency, partnership, or joint venture between CNRI and Licensee.  This
License Agreement does not grant permission to use CNRI trademarks or
trade name in a trademark sense to endorse or promote products or
services of Licensee, or any third party.

8. By clicking on the "ACCEPT" button where indicated, or by copying,
installing or otherwise using Python 1.6.1, Licensee agrees to be
bound by the terms and conditions of this License Agreement.

        ACCEPT


CWI LICENSE AGREEMENT FOR PYTHON 0.9.0 THROUGH 1.2
--------------------------------------------------

Copyright (c) 1991 - 1995, Stichting Mathematisch Centrum Amsterdam,
The Netherlands.  All rights reserved.

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the name of Stichting Mathematisch
Centrum or CWI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior
permission.

STICHTING MATHEMATISCH CENTRUM DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH CENTRUM BE LIABLE
FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

ZERO-CLAUSE BSD LICENSE FOR CODE IN THE PYTHON DOCUMENTATION
----------------------------------------------------------------------

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

# ################################################################################################################################
# ################################################################################################################################

# cache for by mkpath() -- in addition to cheapening redundant calls,
# eliminates redundant "creating /foo/bar/baz" messages in dry-run mode
_path_created = {}

# ################################################################################################################################
# ################################################################################################################################

def mkpath(name, mode=0o777, verbose=1, dry_run=0): # type: ignore
    """Create a directory and any missing ancestor directories.

    If the directory already exists (or if 'name' is the empty string, which
    means the current directory, which of course exists), then do nothing.
    Raise DistutilsFileError if unable to create some directory along the way
    (eg. some sub-path exists, but is a file rather than a directory).
    If 'verbose' is true, print a one-line summary of each mkdir to stdout.
    Return the list of directories actually created.
    """

    global _path_created

    # Detect a common bug -- name is None
    if not isinstance(name, str):
        raise Exception("mkpath: 'name' must be a string (got %r)" % (name,))

    # XXX what's the better way to handle verbosity? print as we create
    # each directory in the path (the current behaviour), or only announce
    # the creation of the whole path? (quite easy to do the latter since
    # we're not using a recursive algorithm)

    name = os.path.normpath(name)
    created_dirs = []
    if os.path.isdir(name) or name == '':
        return created_dirs
    if _path_created.get(os.path.abspath(name)):
        return created_dirs

    (head, tail) = os.path.split(name)
    tails = [tail]                      # stack of lone dirs to create

    while head and tail and not os.path.isdir(head):
        (head, tail) = os.path.split(head)
        tails.insert(0, tail)          # push next higher dir onto stack

    # now 'head' contains the deepest directory that already exists
    # (that is, the child of 'head' in 'name' is the highest directory
    # that does *not* exist)
    for d in tails:
        #print "head = %s, d = %s: " % (head, d),
        head = os.path.join(head, d)
        abs_head = os.path.abspath(head)

        if _path_created.get(abs_head):
            continue

        if verbose >= 1:
            logger.info("creating %s", head)

        if not dry_run:
            try:
                os.mkdir(head, mode)
            except OSError as exc:
                if not (exc.errno == errno.EEXIST and os.path.isdir(head)): # type: ignore
                    raise Exception("could not create '%s': %s" % (head, exc.args[-1]))
            created_dirs.append(head)

        _path_created[abs_head] = 1
    return created_dirs

# ################################################################################################################################
# ################################################################################################################################

def copy_tree(src, dst, preserve_mode=1, preserve_times=1, # type: ignore
              preserve_symlinks=0, update=0, verbose=1, dry_run=0): # type: ignore
    """Copy an entire directory tree 'src' to a new location 'dst'.

    Both 'src' and 'dst' must be directory names.  If 'src' is not a
    directory, raise DistutilsFileError.  If 'dst' does not exist, it is
    created with 'mkpath()'.  The end result of the copy is that every
    file in 'src' is copied to 'dst', and directories under 'src' are
    recursively copied to 'dst'.  Return the list of files that were
    copied or might have been copied, using their output name.  The
    return value is unaffected by 'update' or 'dry_run': it is simply
    the list of all files under 'src', with the names changed to be
    under 'dst'.

    'preserve_mode' and 'preserve_times' are the same as for
    'copy_file'; note that they only apply to regular files, not to
    directories.  If 'preserve_symlinks' is true, symlinks will be
    copied as symlinks (on platforms that support them!); otherwise
    (the default), the destination of the symlink will be copied.
    'update' and 'verbose' are the same as for 'copy_file'.
    """

    if not dry_run and not os.path.isdir(src):
        raise Exception("cannot copy tree '%s': not a directory" % src)
    try:
        names = os.listdir(src)
    except OSError as e:
        if dry_run:
            names = []
        else:
            raise Exception("error listing files in '%s': %s" % (src, e.strerror))

    if not dry_run:
        mkpath(dst, verbose=verbose) # type: ignore

    outputs = []

    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        if n.startswith('.nfs'):
            # skip NFS rename files
            continue

        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            if verbose >= 1:
                logger.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        elif os.path.isdir(src_name):
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          verbose=verbose, dry_run=dry_run))
        else:
            copy_file(src_name, dst_name, preserve_mode, # type: ignore
                      preserve_times, update, verbose=verbose,
                      dry_run=dry_run)
            outputs.append(dst_name)

    return outputs

# ################################################################################################################################
# ################################################################################################################################

def _copy_file_contents(src, dst, buffer_size=16*1024): # type: ignore
    """Copy the file 'src' to 'dst'; both must be filenames.  Any error
    opening either file, reading from 'src', or writing to 'dst', raises
    DistutilsFileError.  Data is read/written in chunks of 'buffer_size'
    bytes (default 16k).  No attempt is made to handle anything apart from
    regular files.
    """
    # Stolen from shutil module in the standard library, but with
    # custom error-handling added.
    fsrc = None
    fdst = None
    try:
        try:
            fsrc = open(src, 'rb')
        except OSError as e:
            raise Exception("could not open '%s': %s" % (src, e.strerror))

        if os.path.exists(dst):
            try:
                os.unlink(dst)
            except OSError as e:
                raise Exception("could not delete '%s': %s" % (dst, e.strerror))

        try:
            fdst = open(dst, 'wb')
        except OSError as e:
            raise Exception("could not create '%s': %s" % (dst, e.strerror))

        while True:
            try:
                buf = fsrc.read(buffer_size)
            except OSError as e:
                raise Exception("could not read from '%s': %s" % (src, e.strerror))

            if not buf:
                break

            try:
                fdst.write(buf) # type: ignore
            except OSError as e:
                raise Exception("could not write to '%s': %s" % (dst, e.strerror))
    finally:
        if fdst:
            fdst.close()
        if fsrc:
            fsrc.close()

# ################################################################################################################################
# ################################################################################################################################

def copy_file(src, dst, preserve_mode=1, preserve_times=1, update=0, # type: ignore
              link=None, verbose=1, dry_run=0): # type: ignore
    """Copy a file 'src' to 'dst'.  If 'dst' is a directory, then 'src' is
    copied there with the same name; otherwise, it must be a filename.  (If
    the file exists, it will be ruthlessly clobbered.)  If 'preserve_mode'
    is true (the default), the file's mode (type and permission bits, or
    whatever is analogous on the current platform) is copied.  If
    'preserve_times' is true (the default), the last-modified and
    last-access times are copied as well.  If 'update' is true, 'src' will
    only be copied if 'dst' does not exist, or if 'dst' does exist but is
    older than 'src'.

    'link' allows you to make hard links (os.link) or symbolic links
    (os.symlink) instead of copying: set it to "hard" or "sym"; if it is
    None (the default), files are copied.  Don't set 'link' on systems that
    don't support it: 'copy_file()' doesn't check if hard or symbolic
    linking is available. If hardlink fails, falls back to
    _copy_file_contents().

    Under Mac OS, uses the native file copy function in macostools; on
    other systems, uses '_copy_file_contents()' to copy file contents.

    Return a tuple (dest_name, copied): 'dest_name' is the actual name of
    the output file, and 'copied' is true if the file was copied (or would
    have been copied, if 'dry_run' true).
    """

    from stat import ST_ATIME, ST_MTIME, ST_MODE, S_IMODE

    if not os.path.isfile(src):
        raise Exception("can't copy '%s': doesn't exist or not a regular file" % src)

    if os.path.isdir(dst):
        dir = dst
        dst = os.path.join(dst, os.path.basename(src))
    else:
        dir = os.path.dirname(dst)

    if False and update and not newer(src, dst):
        if verbose >= 1:
            logger.debug("not copying %s (output up-to-date)", src)
        return (dst, 0)

    try:
        # for generating verbose output in 'copy_file()'
        _copy_action = { None:   'copying',
                 'hard': 'hard linking',
                 'sym':  'symbolically linking' }
        action = _copy_action[link]
    except KeyError:
        raise ValueError("invalid value '%s' for 'link' argument" % link)

    if verbose >= 1:
        if os.path.basename(dst) == os.path.basename(src):
            logger.info("%s %s -> %s", action, src, dir)
        else:
            logger.info("%s %s -> %s", action, src, dst)

    if dry_run:
        return (dst, 1)

    # If linking (hard or symbolic), use the appropriate system call
    # (Unix only, of course, but that's the caller's responsibility)
    elif link == 'hard':
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):
            try:
                os.link(src, dst)
                return (dst, 1)
            except OSError:
                # If hard linking fails, fall back on copying file
                # (some special filesystems don't support hard linking
                #  even under Unix, see issue #8876).
                pass
    elif link == 'sym':
        if not (os.path.exists(dst) and os.path.samefile(src, dst)):
            os.symlink(src, dst)
            return (dst, 1)

    # Otherwise (non-Mac, not linking), copy the file contents and
    # (optionally) copy the times and mode.
    _copy_file_contents(src, dst)
    if preserve_mode or preserve_times:
        st = os.stat(src)

        # According to David Ascher <da@ski.org>, utime() should be done
        # before chmod() (at least under NT).
        if preserve_times:
            os.utime(dst, (st[ST_ATIME], st[ST_MTIME]))
        if preserve_mode:
            os.chmod(dst, S_IMODE(st[ST_MODE]))

    return (dst, 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    bin_dir = os.path.dirname(sys.executable)

    base_dir = os.path.join(bin_dir, '..')
    base_dir = os.path.abspath(base_dir)

    command = sys.argv[1]

    env_manager = EnvironmentManager(base_dir, bin_dir)
    func = getattr(env_manager, command)
    func()

# ################################################################################################################################
# ################################################################################################################################
