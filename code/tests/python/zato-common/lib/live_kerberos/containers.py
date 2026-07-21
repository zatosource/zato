# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import subprocess
from time import sleep, time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Docker details of the KDC the live tests run against
    KDC_Image          = 'debian:12-slim'
    KDC_Container_Name = 'zato-test-kdc'
    KDC_Port           = 8788

    # The test realm and its principals
    Realm             = 'ZATO.TEST'
    Client_Principal  = 'zato-client@ZATO.TEST'
    Service_Principal = 'HTTP/localhost@ZATO.TEST'

    # The service principal in the host-based form that GSSAPI names use
    Service_SPN = 'HTTP@localhost'

    # A principal that exists nowhere, for negative tests
    Wrong_Principal = 'zato-wrong@ZATO.TEST'

    # The directory shared between the container and the host - the container writes
    # the keytabs and the readiness marker into it. The path is fixed so that server
    # processes can point KRB5_CONFIG at it before the KDC even runs.
    Shared_Dir = '/tmp/zato-test-kerberos'

    # Where the host-side krb5.conf is written - this is the file KRB5_CONFIG points to
    Krb5_Config_Path = os.path.join(Shared_Dir, 'krb5.conf')

    # Keytabs the container exports for the host to use
    Client_Keytab_Path  = os.path.join(Shared_Dir, 'client.keytab')
    Service_Keytab_Path = os.path.join(Shared_Dir, 'service.keytab')

    # The marker file the container touches once provisioning is complete
    Ready_Marker_Path = os.path.join(Shared_Dir, 'ready')

    # How long to wait for the container to provision itself - the first run
    # includes an apt-get install, which is the slow part.
    Ready_Timeout = 300

    # How long to sleep between readiness checks
    Ready_Sleep = 1

    # After how many checks the wait reports its progress
    Ready_Report_Every = 15

# ################################################################################################################################
# ################################################################################################################################

# The krb5.conf the host uses - the KDC port is the published one and UDP is disabled
# because Docker forwards the TCP port reliably. The credential cache lives in the shared
# directory so that recreating the KDC also discards tickets from its previous incarnation.
_krb5_conf_host = f"""
[libdefaults]
    default_realm = {ModuleCtx.Realm}
    dns_lookup_kdc = false
    dns_lookup_realm = false
    udp_preference_limit = 1
    default_ccache_name = FILE:{ModuleCtx.Shared_Dir}/ccache

[realms]
    {ModuleCtx.Realm} = {{
        kdc = localhost:{ModuleCtx.KDC_Port}
    }}
"""

# The krb5.conf the container itself uses - inside, the KDC listens on the standard port
_krb5_conf_container = f"""
[libdefaults]
    default_realm = {ModuleCtx.Realm}
    dns_lookup_kdc = false
    dns_lookup_realm = false

[realms]
    {ModuleCtx.Realm} = {{
        kdc = localhost:88
    }}
"""

# The KDC profile the container uses
_kdc_conf = f"""
[kdcdefaults]
    kdc_ports = 88
    kdc_tcp_ports = 88

[realms]
    {ModuleCtx.Realm} = {{
        database_name = /var/lib/krb5kdc/principal
        key_stash_file = /var/lib/krb5kdc/stash
        max_life = 12h 0m 0s
        max_renewable_life = 7d 0h 0m 0s
    }}
"""

# The script the container runs - it installs the KDC, provisions the realm,
# exports the keytabs, reports readiness and serves in the foreground.
_provision_script = f"""#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y -qq krb5-kdc krb5-admin-server > /dev/null

export KRB5_CONFIG=/shared/krb5.container.conf
export KRB5_KDC_PROFILE=/shared/kdc.conf

kdb5_util create -s -r {ModuleCtx.Realm} -P zato.test.master

kadmin.local -r {ModuleCtx.Realm} -q 'addprinc -randkey {ModuleCtx.Client_Principal}'
kadmin.local -r {ModuleCtx.Realm} -q 'addprinc -randkey {ModuleCtx.Service_Principal}'

kadmin.local -r {ModuleCtx.Realm} -q 'ktadd -k /shared/client.keytab {ModuleCtx.Client_Principal}'
kadmin.local -r {ModuleCtx.Realm} -q 'ktadd -k /shared/service.keytab {ModuleCtx.Service_Principal}'

chmod 644 /shared/client.keytab /shared/service.keytab

touch /shared/ready

exec krb5kdc -n
"""

# ################################################################################################################################
# ################################################################################################################################

def _remove_stale_container() -> 'None':
    """ Removes a container left over from a previous, possibly interrupted, run.
    """
    _ = subprocess.run(['docker', 'rm', '-f', ModuleCtx.KDC_Container_Name], capture_output=True, check=False)

# ################################################################################################################################

def stop_kdc() -> 'None':
    """ Stops the KDC container - it removes itself because it was started with --rm.
    """
    _ = subprocess.run(['docker', 'stop', ModuleCtx.KDC_Container_Name], capture_output=True, check=False)

# ################################################################################################################################

def _write_shared_files() -> 'None':
    """ Prepares the shared directory with the configuration the container and the host need.
    """
    # Start from a clean slate so stale keytabs or markers from previous runs do not linger
    shutil.rmtree(ModuleCtx.Shared_Dir, ignore_errors=True)
    os.makedirs(ModuleCtx.Shared_Dir, exist_ok=True)

    file_map = {
        ModuleCtx.Krb5_Config_Path: _krb5_conf_host,
        os.path.join(ModuleCtx.Shared_Dir, 'krb5.container.conf'): _krb5_conf_container,
        os.path.join(ModuleCtx.Shared_Dir, 'kdc.conf'): _kdc_conf,
    }

    for path, contents in file_map.items():
        with open(path, 'w') as file_:
            _ = file_.write(contents)

    script_path = os.path.join(ModuleCtx.Shared_Dir, 'provision.sh')

    with open(script_path, 'w') as file_:
        _ = file_.write(_provision_script)

    os.chmod(script_path, 0o755)

# ################################################################################################################################

def _wait_until_ready() -> 'None':
    """ Waits until the container reports that the realm and the keytabs are in place.
    """
    deadline = time() + ModuleCtx.Ready_Timeout
    attempt_count = 0

    while time() < deadline:

        if os.path.exists(ModuleCtx.Ready_Marker_Path):
            return

        # The container may have exited with an error, in which case waiting further is pointless
        result = subprocess.run(
            ['docker', 'inspect', '--format', '{{.State.Running}}', ModuleCtx.KDC_Container_Name],
            capture_output=True, text=True, check=False)

        if result.returncode == 0 and result.stdout.strip() != 'true':
            logs = subprocess.run(
                ['docker', 'logs', ModuleCtx.KDC_Container_Name], capture_output=True, text=True, check=False)
            raise Exception(f'The KDC container exited during provisioning -> {logs.stdout}\n{logs.stderr}')

        # The first run pulls the image and installs packages, so a long wait reports that it is still alive
        attempt_count += 1

        if attempt_count % ModuleCtx.Ready_Report_Every == 0:
            print(f'Still waiting for the KDC, attempt {attempt_count}', flush=True)

        sleep(ModuleCtx.Ready_Sleep)

    raise Exception(f'The KDC did not become ready within {ModuleCtx.Ready_Timeout}s')

# ################################################################################################################################

def start_kdc() -> 'None':
    """ Starts an MIT KDC container that provisions the test realm, a client principal
    with an exported keytab and a service principal with its own keytab, both written
    to the fixed shared directory along with the krb5.conf the host uses.
    """
    print(f'Starting the KDC container {ModuleCtx.KDC_Container_Name} on port {ModuleCtx.KDC_Port}', flush=True)

    _remove_stale_container()
    _write_shared_files()

    command:'strlist' = [
        'docker', 'run', '-d', '--rm',
        '--name', ModuleCtx.KDC_Container_Name,
        '-v', f'{ModuleCtx.Shared_Dir}:/shared',
        '-p', f'{ModuleCtx.KDC_Port}:88',
        '-p', f'{ModuleCtx.KDC_Port}:88/udp',
        ModuleCtx.KDC_Image,
        '/shared/provision.sh',
    ]

    _ = subprocess.run(command, check=True, capture_output=True)

    print('Waiting for the KDC container to provision the realm', flush=True)
    _wait_until_ready()
    print('The KDC container is ready', flush=True)

# ################################################################################################################################
# ################################################################################################################################
