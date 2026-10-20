# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import tuple_

# ################################################################################################################################
# ################################################################################################################################

# The interface every development SFTP server listens on
Bind_Host = '0.0.0.0'

# The OpenSSH server image every development SFTP server runs in
Container_Image = 'atmoz/sftp:alpine'

# What the container of each development server is named, followed by its port
Container_Name_Prefix = 'zato-sftp-dev-'

# Fixed ports for the three development servers
Port_Password_User1 = 33101
Port_Password_User2 = 33102
Port_Public_Key_User3 = 33103

# Credentials for the password-based servers
User1_Username = 'user1'
User1_Password = 'password1'

User2_Username = 'user2'
User2_Password = 'password2'

# The account that accepts only the login user's public keys
User3_Username = 'user3'

# Where the servers keep their host keys and served files unless overridden
Default_Data_Dir_Name = '.zato-sftp-dev'

# Public key file names checked under the login user's ~/.ssh directory
Login_User_Public_Key_Names = (
    'id_ed25519.pub',
    'id_rsa.pub',
    'id_ecdsa.pub',
)

# ################################################################################################################################
# ################################################################################################################################

User1_Sample_Directories = (
    'Test',
    'Inbound',
    'Outbound',
)

User1_Sample_Files = {
    'Test/README.txt':
        'Connectivity and schema validation uploads.\n',
    'Test/DEMO_20261020_MC_001_01.txt':
        'Sample flat file for the test folder.\n',
    'Inbound/README.txt':
        'Production inbound batches. Upload with a temporary suffix, then rename when complete.\n',
    'Inbound/DEMO_20261020_837P_001_01.txt':
        'Placeholder inbound batch file.\n',
    'Outbound/README.txt':
        'Acknowledgments and status reports after processing.\n',
    'Outbound/sample_functional_ack.txt':
        'Sample acknowledgment file for outbound polling.\n',
}

User2_Sample_Directories = (
    'Incoming',
    'Outgoing',
)

User2_Sample_Files = {
    'Incoming/README.txt':
        'Inbound bulk files from the partner.\n',
    'Incoming/DEMO_Consent_Opt_Out_10202026.csv':
        'patient_id,consent_status,opt_out_date\nP001,opt_out,2026-10-20\n',
    'Outgoing/README.txt':
        'Outbound exception and delta files from the remote side.\n',
    'Outgoing/DEMO_Consent_Exceptions_10202026.csv':
        'patient_id,exception_reason\nP002,duplicate_match\n',
}

User3_Sample_Directories = (
    'inbound/external',
    'inbound/case_management',
    'outbound/reports',
    'work',
)

User3_Sample_Files = {
    'work/README.txt':
        'Development SFTP tree for external dataset and report exchange.\n',
    'inbound/external/sample_measures_2026.csv':
        'measure_id,value,period\nM1,42,2026-Q3\n',
    'inbound/case_management/sample_cases.csv':
        'case_id,status,opened_on\nC100,open,2026-10-01\n',
    'outbound/reports/sample_population_summary.csv':
        'panel,count\nadult,1200\n',
}

# ################################################################################################################################
# ################################################################################################################################

def default_data_dir() -> 'str':
    """ The directory under which every development server stores its files.
    """
    out = os.path.join(os.getcwd(), Default_Data_Dir_Name)
    return out

# ################################################################################################################################

def sample_tree_for_port(port:'int') -> 'tuple_':
    """ The sample directories and files laid out under the given development server port.
    """
    if port == Port_Password_User1:
        out = (User1_Sample_Directories, User1_Sample_Files)
    elif port == Port_Password_User2:
        out = (User2_Sample_Directories, User2_Sample_Files)
    elif port == Port_Public_Key_User3:
        out = (User3_Sample_Directories, User3_Sample_Files)
    else:
        raise Exception('No sample tree is defined for port `{}`'.format(port))

    return out

# ################################################################################################################################
# ################################################################################################################################
