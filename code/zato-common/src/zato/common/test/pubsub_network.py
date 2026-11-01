# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The network of a managed database as the cloud provider runs it, reproduced in the network namespace of its container.
# The connection tracking of the namespace stands for a NAT gateway or a load balancer - it forgets a TCP connection
# that stays idle for the idle limit of the provider, after which the packets of that connection are dropped in both
# directions without notifying either end. A TCP proxy cannot reproduce this, because it terminates the connections
# of the clients and answers their keepalive probes itself. The same tables refuse and delay new connections the way
# an exhausted pool of SNAT ports does, and netem adds the round-trip time of a network between availability zones.

# stdlib
import subprocess

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

# The image with iptables and tc that runs in the network namespace of a container.
_net_image = 'zato-pubsub-test-net:1'
_net_dockerfile = 'FROM alpine:latest\nRUN apk add --no-cache iptables iproute2-tc iproute2-minimal\n'

# The port of the database in its container.
_database_port = 5432

# The chain of the rules that refuse new connections, which is flushed to remove them.
_snat_chain = 'ZATO_SNAT'

# What a percentage is a share of.
_percent_scale = 100

# How many microseconds a millisecond has.
_usec_per_ms = 1000

# ################################################################################################################################
# ################################################################################################################################

def ensure_net_image() -> 'None':
    """ Builds the image with iptables unless it exists already.
    """
    result = subprocess.run(['docker', 'image', 'inspect', _net_image], capture_output=True, check=False)

    if result.returncode != 0:
        dockerfile = _net_dockerfile.encode('utf8')
        _ = subprocess.run(['docker', 'build', '-t', _net_image, '-'], input=dockerfile, capture_output=True, check=True)

# ################################################################################################################################

def run_in_network(container_name:'str', lines:'strlist') -> 'str':
    """ Runs a shell script in the network namespace of a container, with the privileges to change its tables
    and the settings of its connection tracking.
    """
    ensure_net_image()

    script = '\n'.join(lines)
    command = ['docker', 'run', '--rm', '--privileged', '--net', f'container:{container_name}', _net_image, 'sh', '-c', script]

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        raise Exception(f'Script in the network of {container_name} failed with {result.returncode}: {result.stderr.strip()}')

    out = result.stdout
    return out

# ################################################################################################################################
# ################################################################################################################################

def add_round_trip_time(container_name:'str', round_trip_ms:'float') -> 'None':
    """ Delays every packet that leaves the container and every packet that enters it by half of the round-trip time,
    the latter through an ifb device that the ingress traffic is redirected to.
    """
    delay_usec = int(round_trip_ms * _usec_per_ms / 2)

    lines = [
        'set -e',
        f'tc qdisc add dev eth0 root netem delay {delay_usec}us',
        'ip link add ifb0 type ifb',
        'ip link set ifb0 up',
        'tc qdisc add dev eth0 handle ffff: ingress',
        'tc filter add dev eth0 parent ffff: matchall action mirred egress redirect dev ifb0',
        f'tc qdisc add dev ifb0 root netem delay {delay_usec}us',
    ]

    _ = run_in_network(container_name, lines)

# ################################################################################################################################

def install_idle_limit(container_name:'str', idle_seconds:'int') -> 'None':
    """ Makes the network of a container forget a TCP connection to the database once it was idle for idle_seconds,
    and drop the packets of every connection it no longer knows, in both directions.
    """
    lines = [
        'set -e',
        f'echo {idle_seconds} > /proc/sys/net/netfilter/nf_conntrack_tcp_timeout_established',
        'echo 0 > /proc/sys/net/netfilter/nf_conntrack_tcp_loose',
        f'iptables -I INPUT -p tcp --dport {_database_port} -m conntrack --ctstate INVALID -j DROP',
        f'iptables -I OUTPUT -p tcp --sport {_database_port} -m conntrack --ctstate INVALID -j DROP',
    ]

    _ = run_in_network(container_name, lines)

# ################################################################################################################################

def read_dropped_packets(container_name:'str') -> 'int':
    """ Returns how many packets of forgotten connections were dropped so far, in both directions.
    """
    lines = [
        'iptables -L INPUT -v -x -n | awk \'/INVALID/ {sum += $1} END {print sum + 0}\'',
        'iptables -L OUTPUT -v -x -n | awk \'/INVALID/ {sum += $1} END {print sum + 0}\'',
    ]

    output = run_in_network(container_name, lines)

    out = 0
    for value in output.split():
        out += int(value)

    return out

# ################################################################################################################################
# ################################################################################################################################

def install_snat_chain(container_name:'str') -> 'None':
    """ Creates the chain that every new connection to the database passes through and that counts them.
    """
    lines = [
        'set -e',
        f'iptables -N {_snat_chain}',
        f'iptables -I INPUT -p tcp --dport {_database_port} --syn -j {_snat_chain}',
    ]

    _ = run_in_network(container_name, lines)

# ################################################################################################################################

def set_snat_exhaustion(container_name:'str', percent:'int') -> 'None':
    """ Refuses the given percentage of new connections - half of them with a reset, as a NAT that has no port to give
    them, and half of them by dropping their SYN packets, which delays them until the client retransmits.
    """
    # The first rule rejects its share of all new connections and the second one drops the same share
    # of all of them out of those that the first one let through.
    refused = percent / _percent_scale / 2
    dropped = refused / (1 - refused)

    lines = [
        'set -e',
        f'iptables -F {_snat_chain}',
    ]

    if percent:
        reject_rule = f'iptables -A {_snat_chain} -m statistic --mode random --probability {refused:.4f} ' + \
            '-p tcp -j REJECT --reject-with tcp-reset'
        drop_rule = f'iptables -A {_snat_chain} -m statistic --mode random --probability {dropped:.4f} -j DROP'

        lines.append(reject_rule)
        lines.append(drop_rule)

    lines.append(f'iptables -A {_snat_chain} -j RETURN')

    _ = run_in_network(container_name, lines)

# ################################################################################################################################

def read_new_connections(container_name:'str') -> 'int':
    """ Returns how many SYN packets reached the database since the chain was created, including the retransmissions
    of the connections whose SYN packets were dropped.
    """
    lines = [
        f'iptables -L INPUT -v -x -n | awk \'/{_snat_chain}/ {{sum += $1}} END {{print sum + 0}}\'',
    ]

    output = run_in_network(container_name, lines)

    out = int(output.strip())
    return out

# ################################################################################################################################
# ################################################################################################################################
