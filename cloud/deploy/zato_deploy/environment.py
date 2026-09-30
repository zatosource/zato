# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import shutil
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from logging import getLogger

# Zato
from zato_deploy.common import Container, Env_Repo_Layout, EnvRepoConfig, Line_Kind, Link_File, load_env_repo_config, \
    Path, read_env_file, Stage_ID, StageFailed, strlist, strnone
from zato_deploy.git import ensure_key, get_head_commit, read_public_key, run_git
from zato_deploy.state import Progress

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Timestamp_Format = '%Y%m%dT%H%M%S'

_Env_INI_Section = '[env]'
_Project_Root_Key = 'Zato_Project_Root'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Environment:
    """ What the container is started with.
    """
    url:          str
    branch:       str
    commit:       str
    repo_dir:     str
    env_name:     str
    env_dir:      str
    enmasse:      str
    env_ini:      str
    requirements: strnone

# ################################################################################################################################
# ################################################################################################################################

def _write_public_key() -> 'None':
    """ Makes the public half of the deploy key available to the container, so the dashboard can show it.
    """
    ensure_key(Path.Env_Repo_Key)
    public_key = read_public_key(Path.Env_Repo_Key)

    os.makedirs(Path.Link_Dir, exist_ok=True)
    path = os.path.join(Path.Link_Dir, Link_File.Public_Key)

    with open(path, 'w') as output_file:
        _ = output_file.write(public_key + '\n')

    logger.info('Public key written to %s', path)

# ################################################################################################################################

def _get_current_checkout(config:'EnvRepoConfig') -> 'strnone':
    """ Returns the checkout that the link points to if it is of the configured repository and branch, or None otherwise.
    """
    if not os.path.isdir(Path.Env_Repo_Link):
        return None

    repo_dir = os.path.realpath(Path.Env_Repo_Link)

    url_result = run_git(['remote', 'get-url', 'origin'], cwd=repo_dir)
    branch_result = run_git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_dir)

    if url_result.exit_code != 0 or branch_result.exit_code != 0:
        return None

    url    = url_result.stdout.strip()
    branch = branch_result.stdout.strip()

    if url != config.url or branch != config.branch:
        logger.info('Checkout %s is %s at %s, configured is %s at %s', repo_dir, url, branch, config.url, config.branch)
        return None

    return repo_dir

# ################################################################################################################################

def _clone(progress:'Progress', config:'EnvRepoConfig') -> 'str':
    """ Clones the repository into a new directory that the link then points to, and removes the earlier checkouts.
    """
    os.makedirs(Path.Env_Repos_Dir, exist_ok=True)

    timestamp = time.strftime(_Timestamp_Format, time.gmtime())
    repo_dir = os.path.join(Path.Env_Repos_Dir, timestamp)

    progress.log(f'Cloning {config.url} at {config.branch}')
    result = run_git(['clone', '--branch', config.branch, '--single-branch', config.url, repo_dir], is_verbose=True)

    if result.exit_code != 0:
        shutil.rmtree(repo_dir, ignore_errors=True)
        raise StageFailed(f'Repository could not be cloned: {_get_last_line(result.stderr)}')

    # The link is replaced in one step so it never points nowhere ..
    temp_link = Path.Env_Repo_Link + '.new'
    if os.path.lexists(temp_link):
        os.remove(temp_link)
    os.symlink(repo_dir, temp_link)
    os.replace(temp_link, Path.Env_Repo_Link)

    # .. and the checkouts it pointed to before are removed.
    for name in sorted(os.listdir(Path.Env_Repos_Dir)):
        path = os.path.join(Path.Env_Repos_Dir, name)
        if path != repo_dir:
            logger.info('Removing earlier checkout %s', path)
            shutil.rmtree(path, ignore_errors=True)

    return repo_dir

# ################################################################################################################################

def _pull(progress:'Progress', repo_dir:'str') -> 'None':
    """ Brings the checkout up to date, and if that fails, the boot goes on with what the checkout has.
    """
    result = run_git(['pull', '--ff-only'], cwd=repo_dir, is_verbose=True)

    if result.exit_code == 0:
        progress.log(_get_last_line(result.stdout))
    else:
        progress.log(f'Repository could not be updated: {_get_last_line(result.stderr)}', Line_Kind.Error)

# ################################################################################################################################

def _get_last_line(text:'str') -> 'str':

    lines = text.strip().splitlines()

    out = lines[-1] if lines else ''
    return out

# ################################################################################################################################

def _find_env_dir(repo_dir:'str') -> 'str':
    """ Returns the one top-level directory that holds an environment.
    """
    found:'strlist' = []

    for name in sorted(os.listdir(repo_dir)):
        path = os.path.join(repo_dir, name)
        enmasse = os.path.join(path, Env_Repo_Layout.Enmasse)
        if os.path.isfile(enmasse):
            found.append(path)

    if not found:
        raise StageFailed(f'No directory with {Env_Repo_Layout.Enmasse} in the repository')

    if len(found) > 1:
        names:'strlist' = []
        for path in found:
            names.append(os.path.basename(path))
        raise StageFailed(f'More than one directory with {Env_Repo_Layout.Enmasse} in the repository: {", ".join(names)}')

    out = found[0]
    return out

# ################################################################################################################################

def _write_env_ini(env_dir:'str', env_name:'str') -> 'str':
    """ Writes the file that enmasse reads secrets from, with the secrets from cloud-init and the root of the environment
    as the container sees it.
    """
    values = {}

    if os.path.exists(Path.Env_Secrets):
        values = read_env_file(Path.Env_Secrets)

    values[_Project_Root_Key] = os.path.join(Container.Hot_Deploy_Dir, env_name)

    lines = [_Env_INI_Section]
    for key, value in values.items():
        lines.append(f'{key}={value}')

    auto_generated = os.path.join(env_dir, Env_Repo_Layout.Auto_Generated)
    os.makedirs(auto_generated, exist_ok=True)

    out = os.path.join(env_dir, Env_Repo_Layout.Env_INI)

    with open(out, 'w') as output_file:
        _ = output_file.write('\n'.join(lines) + '\n')

    os.chmod(out, 0o600)
    logger.info('env.ini written to %s with keys: %s', out, ', '.join(values))

    return out

# ################################################################################################################################

def _write_current(environment:'Environment') -> 'None':
    """ Tells the dashboard which repository the environment runs.
    """
    data = {
        'url':      environment.url,
        'branch':   environment.branch,
        'commit':   environment.commit,
        'env_name': environment.env_name,
        'time':     datetime.now(timezone.utc).isoformat(),
    }

    path = os.path.join(Path.Link_Dir, Link_File.Current)
    temp_path = path + '.tmp'

    with open(temp_path, 'w') as output_file:
        json.dump(data, output_file, indent=2)

    os.replace(temp_path, path)

# ################################################################################################################################

def prepare_environment(progress:'Progress') -> 'Environment':
    """ Returns the environment from the configured repository, cloned or brought up to date.
    """
    progress.advance_to(Stage_ID.Env_Repo)

    _write_public_key()

    config = load_env_repo_config(Path.Env_Repo_Config)
    logger.info('Repository %s at %s', config.url, config.branch)

    repo_dir = _get_current_checkout(config)

    if repo_dir:
        _pull(progress, repo_dir)
    else:
        repo_dir = _clone(progress, config)

    env_dir = _find_env_dir(repo_dir)
    env_name = os.path.basename(env_dir)

    requirements = os.path.join(env_dir, Env_Repo_Layout.Requirements)
    if not os.path.isfile(requirements):
        requirements = None

    out = Environment()
    out.url          = config.url
    out.branch       = config.branch
    out.commit       = get_head_commit(repo_dir)
    out.repo_dir     = repo_dir
    out.env_name     = env_name
    out.env_dir      = env_dir
    out.enmasse      = os.path.join(env_dir, Env_Repo_Layout.Enmasse)
    out.env_ini      = _write_env_ini(env_dir, env_name)
    out.requirements = requirements

    _write_current(out)

    progress.log(f'Environment {env_name} at {out.commit[:12]}', Line_Kind.OK)

    return out

# ################################################################################################################################
# ################################################################################################################################
