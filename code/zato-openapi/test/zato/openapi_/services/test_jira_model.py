# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.server.service import Model

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class JiraAccessRequestInput(Model):
    issue_key: str
    ssn: str
    company_ssid: str
    mobile_number: str
    email: str
    job_title: str
    access_permit_type: str
    special_authorizations: 'list_[str]'
    company_name: str
    employee: str
    application_type: str
    application_company: str

# ################################################################################################################################
# ################################################################################################################################
