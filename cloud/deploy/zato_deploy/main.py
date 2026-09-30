# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import signal
import time
from logging import getLogger
from types import FrameType

# Zato
from zato_deploy.certificate import obtain_certificate
from zato_deploy.common import Config, load_config, Path, Stage_ID, StageFailed
from zato_deploy.container import build_components, check_environment, ContainerWatch, start_container
from zato_deploy.environment import prepare_environment
from zato_deploy.firewall import add_redirect, keep_redirect_first, remove_redirect
from zato_deploy.host import install_docker, is_docker_installed, prepare_storage, start_docker
from zato_deploy.pull import is_image_present, pull_image
from zato_deploy.run_log import log_host_snapshot, log_run_header, read_restart_reason, setup_logging
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

# How many seconds the download stage takes when only the layers that changed are pulled.
_Update_Download_Weight = 20

# ################################################################################################################################
# ################################################################################################################################

def _handle_sigterm(signal_number:'int', frame:'FrameType | None') -> 'None':
    raise SystemExit(0)

# ################################################################################################################################

def _touch(path:'str') -> 'None':

    directory = os.path.dirname(path)
    os.makedirs(directory, exist_ok=True)

    with open(path, 'w'):
        pass

# ################################################################################################################################

def _remove(path:'str') -> 'None':

    if os.path.exists(path):
        os.remove(path)

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

def _get_image(progress:'Progress', config:'Config') -> 'None':
    """ Pulls the image on every run if updates are on, and otherwise only if there is no image yet.
    """
    is_present = is_image_present(config.image)

    if is_present:
        if config.is_install_updates:
            progress.get_stage(Stage_ID.Download).weight = _Update_Download_Weight
        else:
            progress.remove_stage(Stage_ID.Download)
            progress.log(f'Image {config.image} is present and Zato_Install_Updates is off')
            return

    pull_image(progress, config.image)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    setup_logging(Path.Deploy_Log)
    _ = signal.signal(signal.SIGTERM, _handle_sigterm)

    # The environment is not ready until this run says so ..
    _remove(Path.Ready_Marker)
    reason = read_restart_reason()

    config = load_config(Path.Config)
    is_docker_ready = is_docker_installed()

    stages = build_stages(config.image, is_docker_ready)
    progress = Progress(stages, f'ssh {config.admin_username}@{config.fqdn}')

    log_run_header(config, reason, stages)

    # .. the page lists all the components from the start ..
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
            _touch(Path.Serving_Marker)

            # .. Docker's data goes to the local disk before Docker runs ..
            prepare_storage(progress)

            if not is_docker_ready:
                install_docker(progress)

            # .. and Docker puts its own rules in front of the redirect, which each time goes back to the top ..
            start_docker(progress)
            keep_redirect_first()

            _get_image(progress, config)
            environment = prepare_environment(progress)

            container_ip = start_container(progress, config, environment)
            keep_redirect_first()

            # .. the container runs through its own stages ..
            watch.start()
            _wait_for_container(progress, watch)
            watch.drop_components_not_started()

            # .. and the environment is ready once it answers from outside of the container.
            check_environment(progress, container_ip)
            progress.finish_all()
            watch.stop()

            _touch(Path.Ready_Marker)
            log_host_snapshot('ready')

            time.sleep(_Grace_Period)

        # A failure keeps the page up with the reason in it ..
        except StageFailed as exception:
            progress.fail(exception.message)
            log_host_snapshot('failed')
            _wait_forever()

        except Exception as exception:
            logger.exception('Deployment failed')
            progress.fail(f'Unexpected error: {exception}')
            log_host_snapshot('failed')
            _wait_forever()

    # .. and in either case the port goes back to the Dashboard in the end.
    finally:
        remove_redirect()
        watch.stop()
        if server:
            server.server_close()

# ################################################################################################################################
# ################################################################################################################################
