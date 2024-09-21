# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import glob
import logging
import os
import platform
import sys
from distutils.dir_util import copy_tree
from pathlib import Path
from subprocess import check_output, PIPE, Popen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist, strnone

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

pip_deps_windows     = 'setuptools==57.4.0 wheel'
pip_deps_non_windows = 'setuptools==57.4.0 wheel pip'
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

    def run_pip_install_zato_packages(self, packages:'strlist') -> 'None':

        # All the -e arguments that pip will receive
        pip_args = []

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
            'cython==0.29.32',
            'numpy==1.22.3',
            'pyOpenSSL==23.0.0',
            'zato-ext-bunch==1.2'
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
        packages = [
            'zato-common',
            'zato-agent',
            'zato-broker',
            'zato-cli',
            'zato-client',
            'zato-cy',
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

        self.run_pip_install_zato_packages(packages)

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
