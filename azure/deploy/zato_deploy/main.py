# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import signal
import sys
import time
from logging import getLogger
from types import FrameType

# Zato
from zato_deploy.certificate import obtain_certificate
from zato_deploy.common import load_config, Path, Stage_ID, StageFailed
from zato_deploy.container import build_components, check_environment, ContainerWatch, start_container
from zato_deploy.firewall import add_redirect, keep_redirect_first, remove_redirect
from zato_deploy.host import install_docker, prepare_storage
from zato_deploy.pull import pull_image
from zato_deploy.server import DeployServer, start_server
from zato_deploy.state import build_stages, Progress

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_deploy')

# ################################################################################################################################
# ################################################################################################################################

# How long the page stays after the environment is ready. Each open page polls once a second, so all of them
# learn about it within this time, and the countdown of 2.1 seconds that each then shows ends after the Dashboard took over.
_Grace_Period = 1.2

# How long the container may take from its start until all of its components run.
_Container_Timeout = 1800

# ################################################################################################################################
# ################################################################################################################################

def _handle_sigterm(signal_number:'int', frame:'FrameType | None') -> 'None':
    raise SystemExit(0)

# ################################################################################################################################

def _wait_forever() -> 'None':
    """ Keeps the page up to show what failed, until systemctl stop zato-deploy.
    """
    while True:
        signal.pause()

# ################################################################################################################################

def _wait_for_container(progress:'Progress', watch:'ContainerWatch') -> 'None':

    deadline = time.monotonic() + _Container_Timeout

    while not watch.is_finished():

        if progress.has_failed():
            raise StageFailed('The container failed')

        now = time.monotonic()
        if now > deadline:
            raise StageFailed(f'The container was not ready within {_Container_Timeout} seconds')

        time.sleep(0.5)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', stream=sys.stdout)
    _ = signal.signal(signal.SIGTERM, _handle_sigterm)

    config = load_config(Path.Config)
    stages = build_stages(config.image)
    progress = Progress(stages, f'ssh {config.admin_username}@{config.fqdn}')

    # The page lists all the components from the start ..
    components = build_components()
    progress.get_stage(Stage_ID.Components).components = components
    watch = ContainerWatch(progress, components)

    server:'DeployServer | None' = None

    try:
        try:

            # .. nothing can listen before there is a certificate ..
            pem_path = obtain_certificate(progress, config)
            server = start_server(progress, pem_path)
            add_redirect()

            # .. Docker's data goes to the local disk before Docker exists ..
            prepare_storage(progress)

            # .. and Docker puts its own rules in front of the redirect, which each time goes back to the top ..
            install_docker(progress)
            keep_redirect_first()

            pull_image(progress, config.image)

            container_ip = start_container(progress, config)
            keep_redirect_first()

            # .. the container runs through its own stages ..
            watch.start()
            _wait_for_container(progress, watch)
            watch.drop_components_not_started()

            # .. and the environment is ready once it answers from outside of the container.
            check_environment(progress, container_ip)
            progress.finish_all()
            watch.stop()

            time.sleep(_Grace_Period)

        # A failure keeps the page up with the reason in it ..
        except StageFailed as exception:
            progress.fail(exception.message)
            _wait_forever()

        except Exception as exception:
            logger.exception('Deployment failed')
            progress.fail(f'Unexpected error: {exception}')
            _wait_forever()

    # .. and in either case the port goes back to the Dashboard in the end.
    finally:
        remove_redirect()
        watch.stop()
        if server:
            server.server_close()

# ################################################################################################################################
# ################################################################################################################################
