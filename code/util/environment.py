# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import platform
import sys
from distutils.dir_util import copy_tree
from pathlib import Path
from subprocess import check_output, PIPE, Popen

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

zato_command_template = """
#!{bin_dir}/python

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

# ################################################################################################################################
# ################################################################################################################################

class EnvironmentManager:

    def __init__(self, base_dir, bin_dir):
        # type: (str) -> None
        self.base_dir = base_dir
        self.bin_dir = bin_dir
        self.pip_command = os.path.join(self.bin_dir, 'pip')
        self.python_command = os.path.join(self.bin_dir, 'python')
        self.pip_options = ''

        self.site_packages_dir = 'invalid-site_packages_dir'
        self.eggs_dir = 'invalid-self.eggs_dir'

        self._set_up_pip_flags()
        self._set_up_dir_names()

# ################################################################################################################################

    def _get_linux_distro_name(self):

        # Short-cut for non-Linux systems
        if not is_linux:
            return ''

        # If we are here, it means that we are under a Linux distribution and we assume
        # that the file exists per https://www.freedesktop.org/software/systemd/man/os-release.html

        # By default, we do not have it
        distro_name = ''

        data = open('/etc/os-release').read() # type: str
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

    def _set_up_pip_flags(self):

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

    def _set_up_dir_names(self):

        # This needs to be checked in runtime because we do not know
        # under what Python version we are are going to run.
        py_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
        logger.info('Python version maj.min -> %s', py_version)

        # Under Linux, the path to site-packages contains the Python version but it does not under Windows.
        # E.g. ~/src-zato/lib/python3.8/site-packages vs. C:\src-zato\lib\site-packages
        if is_linux:
            py_lib_dir = 'python' + py_version
        else:
            py_lib_dir = ''

        py_lib_dir = os.path.join(self.base_dir, 'lib', py_lib_dir)
        logger.info('Python lib dir -> %s', py_lib_dir)

        self.site_packages_dir = os.path.join(py_lib_dir, 'site-packages')
        logger.info('Python site-packages dir -> %s', self.site_packages_dir)

        self.eggs_dir = os.path.join(self.base_dir, 'eggs')
        logger.info('Python eggs dir -> %s', self.eggs_dir)

# ################################################################################################################################

    def _create_symlink(self, from_, to):
        # type: (str, str) -> None

        try:
            os.symlink(from_, to)
        except FileExistsError:
            # It is not an issue if it exists, likely install.sh/.bat ran twice.
            pass
        else:
            logger.info('Symlinked from  `%s` to `%s`', from_, to)

# ################################################################################################################################

    def _create_executable(self, path, data):
        # type: (str) -> None

        f = open(path, 'w')
        f.write(data)
        f.close()

        logger.info('Created file `%s`', path)

        # .. and make it executable.
        os.chmod(path, 0o740)

        logger.info('Made file executable `%s`', path)

# ################################################################################################################################

    def run_command(self, command, exit_on_error=True, needs_stdout=False, needs_stderr=False, log_stderr=True,
        use_check_output=False):
        # type: (str) -> str

        logger.info('Running `%s`', command)

        # Turn what is possibly a multi-line command into a list of arguments ..
        command = command.strip()
        command = command.split()

        func = self._run_check_output if use_check_output else self._run_popen
        return func(command, exit_on_error, needs_stdout, needs_stderr, log_stderr)

# ################################################################################################################################

    def _run_check_output(self, command, exit_on_error=True, needs_stdout=False, needs_stderr=False, log_stderr=True):

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

    def _run_popen(self, command, exit_on_error=True, needs_stdout=False, needs_stderr=False, log_stderr=True):

        # This will be potentially returned to our caller
        stdout = None

        # Run the command ..
        process = Popen(command, stderr=PIPE, stdout=PIPE if needs_stdout else None)

        # .. and wait until it completes.
        while True:

            stderr = process.stderr.readline()

            if needs_stdout:
                stdout = process.stdout.readline()
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

    def pip_install_core_pip(self):

        # Set up the command ..
        command = '{pip_command} install {pip_options} -U {pip_deps}'.format(**{
            'pip_command': self.pip_command,
            'pip_options': self.pip_options,
            'pip_deps':    pip_deps,
        })

        # .. and run it.
        self.run_command(command, exit_on_error=False)

# ################################################################################################################################

    def pip_install_requirements(self):

        # Always use full paths to resolve any doubts
        reqs_path = os.path.join(self.base_dir, 'requirements.txt')

        # Set up the command ..
        command = """
            {pip_command}
            install
            {pip_options}
            -r {reqs_path}
        """.format(**{
               'pip_command': self.pip_command,
               'pip_options': self.pip_options,
               'reqs_path':   reqs_path
            })

        # .. and run it.
        self.run_command(command, exit_on_error=False)

# ################################################################################################################################

    def pip_install_zato_packages(self):

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

        # All the -e arguments that pip will receive
        pip_args = []

        # Build the arguments
        for name in packages:
            package_path = os.path.join(self.base_dir, name)
            arg = '-e {}'.format(package_path)
            pip_args.append(arg)

        # Build the command ..
        command = '{} install {}'.format(self.pip_command, ' '.join(pip_args))

        # .. and run it.
        self.run_command(command, exit_on_error=False)

# ################################################################################################################################

    def pip_uninstall(self):

        # Packages that will be uninstalled, e.g. no longer needed
        packages = [
            'imbox',
            'pycrypto',
            'python-keyczar',
        ]

        # Build the command ..
        command = '{} uninstall -y -qq {}'.format(self.pip_command, ' '.join(packages))

        # .. and run it.
        self.run_command(command, exit_on_error=False)

# ################################################################################################################################

    def pip_install(self):
        self.pip_install_core_pip()
        self.pip_install_requirements()
        self.pip_install_zato_packages()
        self.pip_uninstall()

# ################################################################################################################################

    def update_git_revision(self):

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
        f.write(commit_id)
        f.close()

        logger.info('Git commit ID -> `%s`', commit_id)

# ################################################################################################################################

    def add_eggs_symlink(self):

        if not is_windows:
            self._create_symlink(self.site_packages_dir, self.eggs_dir)

# ################################################################################################################################

    def add_extlib(self):

        # This is where external depdendencies can be kept
        extlib_dir_path = os.path.join(self.base_dir, 'extlib')

        # For backward compatibility, this will point to extlib
        extra_paths_dir = os.path.join(self.base_dir, 'zato_extra_paths')

        # This is what the extlib will be found through in runtime
        easy_install_path = os.path.join(self.site_packages_dir, 'easy-install.pth')

        # Build a Path object ..
        extlib_dir = Path(extlib_dir_path)

        # .. create the underlying directory ..
        extlib_dir.mkdir(exist_ok=True)

        # .. symlink it for backward compatibility ..
        self._create_symlink(extlib_dir_path, extra_paths_dir)

        # .. and add the path to easy_install.
        f = open(easy_install_path, 'a')
        f.write(extlib_dir_path)
        f.write(os.linesep)
        f.close()

# ################################################################################################################################

    def add_py_command(self):

        # This is where will will save it
        py_command_path = os.path.join(self.bin_dir, 'py')

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

    def add_zato_command(self):

        # Differentiate between Windows and other systems as the extension is needed under the former
        command_name = 'zato.py' if is_windows else 'zato'

        # This is where the command file will be created
        command_path = os.path.join(self.bin_dir, command_name)

        # Build the full contents of the command file ..
        data = zato_command_template.format(**{
            'base_dir': self.base_dir,
            'bin_dir': self.bin_dir
        })

        # .. and add the file to the file system.
        self._create_executable(command_path, data)

# ################################################################################################################################

    def copy_patches(self):

        # Where our patches can be found
        patches_dir = os.path.join(self.base_dir, 'patches')

        # Where to copy them to
        dest_dir = self.site_packages_dir

        logger.info('Copying patches from %s -> %s', patches_dir, dest_dir)

        # Recursively copy all the patches, overwriting any files found
        copy_tree(patches_dir, dest_dir, preserve_symlinks=True, verbose=1)

        logger.info('Copied patches from %s -> %s', patches_dir, dest_dir)

# ################################################################################################################################

    def install(self):

        self.update_git_revision()
        self.pip_install()
        self.add_eggs_symlink()
        self.add_extlib()
        self.add_py_command()
        self.add_zato_command()
        self.copy_patches()

# ################################################################################################################################

    def update(self):

        self.update_git_revision()
        self.pip_install()
        self.copy_patches()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    bin_dir = os.path.dirname(sys.executable)

    base_dir = os.path.join(bin_dir, '..')
    base_dir = os.path.abspath(base_dir)

    command = sys.argv[1]

    util = EnvironmentManager(base_dir, bin_dir)
    func = getattr(util, command)
    func()

# ################################################################################################################################
# ################################################################################################################################
