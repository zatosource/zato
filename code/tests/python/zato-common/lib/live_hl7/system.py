# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass

# Live HL7
from live_hl7.compose import ComposeStack
from live_hl7.credentials import No_Rules
from live_hl7.ports import PortPlan

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strintdict, strlist, strstrdict, strtuple

# ################################################################################################################################
# ################################################################################################################################

# Every system publishes on this address
Host = '127.0.0.1'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Handle:
    """ A started system - what a test or a command needs to talk to it and to stop it.
    """
    system: str
    project_name: str
    ports: 'strintdict'
    images: 'strstrdict'
    password: str
    started_at: str
    is_standalone: bool
    stack: 'ComposeStack'

# ################################################################################################################################

    def port(self, purpose:'str') -> 'int':
        out = self.ports[purpose]
        return out

# ################################################################################################################################

    def address(self, purpose:'str') -> 'str':
        port = self.ports[purpose]

        out = f'{Host}:{port}'
        return out

# ################################################################################################################################

    def http_url(self, purpose:'str') -> 'str':
        address = self.address(purpose)

        out = f'http://{address}'
        return out

# ################################################################################################################################

    def https_url(self, purpose:'str') -> 'str':
        address = self.address(purpose)

        out = f'https://{address}'
        return out

# ################################################################################################################################
# ################################################################################################################################

class LiveSystem:
    """ What every system provides - its compose file, the ports it publishes, how it says it is ready
    and what has to happen once it is.
    """

    # The system's short name, also its directory, its state file and its part of the make targets
    name = ''

    # Which block above the port base the system takes when it runs standalone - unique across every system
    block_number = 0

    # The purposes of the ports it publishes, in the order of its standalone block
    purposes:'strtuple' = ()

    # What the system requires of a password set through it
    password_rules = No_Rules

    # Service name to image, as written in the compose file
    images:'strstrdict' = {}

    # Volumes that outlive the stack, declared external in the compose file and created before the first start
    kept_volumes:'strtuple' = ()

    # Services that do their work and exit on purpose, whose exit is not the system going down
    one_off_services:'strtuple' = ()

    # The directory holding compose.yml and everything the compose file mounts
    directory = ''

    # What a person sees under describe
    summary = ''

    # Where a person opens the system's own UI once it runs - the purpose whose port the URL uses, the path under
    # it, whether it is HTTPS, and who logs in, the password being the one every system is started with. A system
    # with no UI of its own leaves the purpose empty.
    ui_purpose = ''
    ui_path = ''
    ui_is_https = False
    ui_username = ''

# ################################################################################################################################

    def follow_logs(self, handle:'Handle') -> 'None':
        """ Streams what the system logs until interrupted - its containers' output unless the system says otherwise.
        """
        handle.stack.follow_logs()

# ################################################################################################################################

    def ui_url(self, handle:'Handle') -> 'str':
        """ The address a person opens the system's UI at, empty for a system without one.
        """
        if not self.ui_purpose:
            return ''

        if self.ui_is_https:
            root = handle.https_url(self.ui_purpose)
        else:
            root = handle.http_url(self.ui_purpose)

        out = root + self.ui_path
        return out

# ################################################################################################################################

    def compose_path(self) -> 'str':
        out = os.path.join(self.directory, 'compose.yml')
        return out

# ################################################################################################################################

    def port_plan(self) -> 'PortPlan':
        out = PortPlan(self.name, self.block_number, self.purposes)
        return out

# ################################################################################################################################

    def environment(self, ports:'strintdict', password:'str') -> 'strstrdict':
        """ The placeholders the compose file interpolates - a port per purpose and the password.
        """
        prefix = self.name.upper()

        out:'strstrdict' = {}

        for purpose, port in ports.items():
            out[f'{prefix}_{purpose.upper()}_PORT'] = str(port)

        out[f'{prefix}_PASSWORD'] = password

        return out

# ################################################################################################################################

    def prepare(self, handle:'Handle') -> 'None':
        """ Runs before the containers start - fetches and renders whatever the compose file mounts.
        """

# ################################################################################################################################

    def after_start(self, handle:'Handle') -> 'None':
        """ Runs once the containers are up and before the system is waited for - database seeding
        the system cannot do for itself.
        """

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        """ True once the system answers the way a client of it expects.
        """
        raise Exception(f'{self.name} does not say when it is ready')

# ################################################################################################################################

    def after_ready(self, handle:'Handle') -> 'None':
        """ Runs once, right after the system is ready - password changes and first-start setup.
        """

# ################################################################################################################################

    def describe(self, ports:'strintdict') -> 'str':
        """ The system, its images and the ports it takes.
        """
        lines:'strlist' = [self.summary, '']

        for service, image in self.images.items():
            lines.append(f'  {service:<18} {image}')

        if self.purposes:
            lines.append('')
            plan = self.port_plan()
            lines.append(plan.describe(ports))

        out = '\n'.join(lines)
        return out

# ################################################################################################################################
# ################################################################################################################################
