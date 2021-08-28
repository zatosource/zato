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
from pathlib import Path
from subprocess import CalledProcessError, PIPE, Popen, run as subprocess_run

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################



# ################################################################################################################################
# ################################################################################################################################

class InstallUtil:
    """ Tasks run after the main installation process.
    """
    def __init__(self, base_dir, bin_dir):
        # type: (str) -> None
        self.base_dir = base_dir
        self.bin_dir = bin_dir
        self.pip_command = os.path.join(self.bin_dir, 'pip')
        self.python_command = os.path.join(self.bin_dir, 'python')

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

    def run_command(self, command, exit_on_error=True, needs_stdout=False):
        # type: (str) -> str

        logger.info('Running `%s`', command)

        # Turn what is possibly a multi-line command into a list of arguments ..
        command = command.strip()
        command = command.split()

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
                logger.warn(stderr)

                if exit_on_error:
                    process.kill()
                    sys.exit(1)

            if process.poll() is not None:
                break

        if needs_stdout:
            return stdout

# ################################################################################################################################

    def pip_install_core_pip(self):

        # Set up the command ..
        command = '{} install --no-warn-script-location -U setuptools pip'.format(self.pip_command)

        # .. and run it.
        self.run_command(command)

# ################################################################################################################################

    def pip_install_requirements(self):

        # Always use full paths to resolve any doubts
        reqs_path = os.path.join(self.base_dir, 'requirements.txt')

        # Set up the command ..
        command = """
            {} install
            --no-warn-script-location
            -r {}
        """.format(self.pip_command, reqs_path)

        # .. and run it.
        self.run_command(command)

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
        self.run_command(command)

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
        self.run_command(command)

# ################################################################################################################################

    def update_git_revision(self):

        # This is where we will store our last git commit ID
        revision_file_path = os.path.join(self.base_dir, 'release-info', 'revision.txt')

        # Build the command ..
        command = 'git log -n 1 --pretty=format:%H --no-color'

        # .. run the command to get our latest commit ID ..
        commit_id = self.run_command(command, needs_stdout=True)

        # .. and store it in an external file for 'zato --version' and other tools to use.
        f = open(revision_file_path, 'w')
        f.write(commit_id)
        f.close()

# ################################################################################################################################

    def add_eggs_symlink(self):

        # This needs to be checked in runtime because we do not know
        # under what Python version we are are going to run.
        py_version = '{}.{}'.format(sys.version_info.major, sys.version_info.minor)
        logger.info('Python version maj.min -> %s', py_version)

        py_lib_dir = 'python' + py_version
        py_lib_dir = os.path.join(self.base_dir, 'lib', py_lib_dir)
        logger.info('Python lib dir -> %s', py_lib_dir)

        site_packages_dir = os.path.join(py_lib_dir, 'site-packages')
        logger.info('Python site-packages dir -> %s', site_packages_dir)

        eggs_dir = os.path.join(self.base_dir, 'eggs')
        logger.info('Python eggs dir -> %s', eggs_dir)

        self._create_symlink(site_packages_dir, eggs_dir)

# ################################################################################################################################

    def add_py_command(self):

        # This is where will will save it
        py_command_path = os.path.join(self.bin_dir, 'py')

        # There will be two versions, one for Windows and one for other systems

        #
        # Windows
        #
        if 'windows' in platform.system().lower():
            template = ''
            template += '"{}" %*'

        # Non-Windows
        else:
            template = ''
            template += '#!/bin/sh'
            template = '\n'
            template += '"{}" "$@"'

        # Add the full path to the OS-specific template ..
        data = template.format(self.python_command)

        # .. add the file to the system ..
        f = open(py_command_path, 'w')
        f.write(data)
        f.close()

        # .. and make it executable.
        os.chmod(py_command_path, 0o740)

# ################################################################################################################################

    def add_extlib(self):

        # This is where external depdendencies can be kept
        extlib_dir_path = os.path.join(self.base_dir, 'extlib')

        # For backward compatibility, this will point to extlib
        extra_paths_dir = os.path.join(self.base_dir, 'zato_extra_paths')

        # This is what the extlib will be found through in runtime
        easy_install_path = os.path.join(self.base_dir, 'eggs', 'easy-install.pth')

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

    def run(self):

        '''
        self.update_git_revision()

        self.pip_install_core_pip()
        self.pip_install_requirements()
        self.pip_install_zato_packages()
        self.pip_uninstall()

        self.add_eggs_symlink()
        self.add_py_command()
        self.add_extlib()
        '''

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    bin_dir = os.path.dirname(sys.executable)

    base_dir = os.path.join(bin_dir, '..')
    base_dir = os.path.abspath(base_dir)

    util = InstallUtil(base_dir, bin_dir)
    util.run()

# ################################################################################################################################
# ################################################################################################################################
