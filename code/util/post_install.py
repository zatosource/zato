# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import logging
import sys
from subprocess import CalledProcessError, PIPE, Popen, run as subprocess_run

# ################################################################################################################################
# ################################################################################################################################

log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)

logger = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class PostInstallProcess:
    """ Tasks run after the main installation process.
    """
    def __init__(self, base_dir):
        # type: (str) -> None
        self.base_dir = base_dir

# ################################################################################################################################

    def run_command(self, command, exit_on_error=True):
        # type: (str) -> str

        logger.info('Running `%s`', command)

        # Turn what is possibly a multi-line command into a list of arguments ..
        command = command.strip()
        command = command.split()

        process = Popen(command, stdout=PIPE, stderr=PIPE)

        while True:
            stdout = process.stdout.readline()
            stderr = process.stderr.readline()

            if stdout:
                stdout = stdout.strip()
                stdout = stdout.decode('utf8')
                logger.info(stdout)

            if stderr:
                stderr = stderr.strip()
                stderr = stderr.decode('utf8')
                logger.warn(stderr)

            if process.poll() is not None:
                break

        #rc = process.poll()
        #return rc

        '''
        try:
            out = subprocess_run(command, check=True, stdout=PIPE, stderr=PIPE)
        except CalledProcessError as e:
            stderr = e.stderr.decode('utf8').strip()
            msg = 'Error while executing command `{}` -> `{}`\n'.format(command, stderr)
            sys.stderr.write(msg)
            sys.exit(1)

        print()
        print(222, command)
        print()
        '''

# ################################################################################################################################

    def update_git_revision(self):

        # sh
        import sh

        # This is where we will store our last git commit ID
        revision_file_path = os.path.join(self.base_dir, 'release-info', 'revision.txt')

        #out = sh.pip('install', 'gevent')

        # Invoke git ..
        out = sh.git('log', '-n', '1', '--pretty=format:%H', '--no-color')

        # .. get our latest commit ID (we use repr because out.stdout may contain shell escape codes) ..
        commit_id = repr(out)

        # .. and store it in an external file for 'zato --version' and other tools to use.
        f = open(revision_file_path, 'w')
        f.write(commit_id)
        f.close()

# ################################################################################################################################

    def pip_install_requirements(self):

        # Core pip dependencies ..
        command = 'pip install --no-warn-script-location -U setuptools pip'

        # .. run the command ..
        self.run_command(command)


# ################################################################################################################################

    def run(self):
        self.pip_install_requirements()
        # self.update_git_revision()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    sys_exec_dir = os.path.dirname(sys.executable)

    base_dir = os.path.join(sys_exec_dir, '..')
    base_dir = os.path.abspath(base_dir)

    process = PostInstallProcess(base_dir)
    process.run()

# ################################################################################################################################
# ################################################################################################################################
