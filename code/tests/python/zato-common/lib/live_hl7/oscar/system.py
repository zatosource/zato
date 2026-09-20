# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tarfile
from base64 import b64encode
from functools import partial
from http.client import OK
from io import BytesIO
from secrets import token_bytes

# cryptography - the one dependency outside the standard library, for the upload protocol's RSA and AES
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

# Live HL7
from live_containers.ready import wait_until
from live_hl7.credentials import PasswordRules
from live_hl7.fetch import fetch_once, work_directory
from live_hl7.http import FileField, Session, expect_status, request
from live_hl7.system import Handle, LiveSystem

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strintdict, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# Service names in the compose file
Webapp_Service = 'oscar'
DB_Service = 'db'

# The account the database scripts create, with the password the scripts announce and the PIN they set
Default_Username = 'openodoc'
Default_Initial_Password = 'openo2025'
Default_PIN = '2025'

# The database the scripts create and the account the properties file connects with
Database_Name = 'oscar'
Database_User = 'root'

# Where the properties come from - the open-osp commit the image was built from
Open_OSP_Commit = '030707714cc9b277db9be26356faccb511c5f947'
Open_OSP_Raw = f'https://raw.githubusercontent.com/open-osp/open-osp/{Open_OSP_Commit}/docker/oscar/conf'
Properties_URL = f'{Open_OSP_Raw}/oscar_mcmaster_bc.properties'
Drugref_URL = f'{Open_OSP_Raw}/drugref2.properties'

# What is cached and rendered on the host
Properties_Cache_Name = 'oscar-properties-bc.properties'
Drugref_Cache_Name = 'oscar-drugref2.properties'
Config_Dir_Name = 'oscar-config'
Scripts_Dir_Name = 'oscar-mysql-scripts'

# Where the image keeps the database scripts and where the database container sees them
Image_Scripts_Dir = '/oscar-mysql-scripts'
DB_Scripts_Dir = '/oscar-mysql-scripts'
Create_Database_Script = 'createdatabase_bc.sh'

# Where OSCAR sends an ADT^A04 for every demographic it creates - the host is always ours, the port is set by
# the environment so a test can listen there
A04_Port_Env = 'Zato_HL7_Live_Oscar_A04_Port'
A04_Default_Port = 30987
A04_Host = 'host.docker.internal'

# Browser paths
Context_Path = '/oscar'
Login_Page = Context_Path + '/index.jsp'
Login_Action = Context_Path + '/login.do'
Lab_Upload_Action = Context_Path + '/lab/newLabUpload.do'

# The handler types of the lab upload the properties enable
Lab_Type_PathNet = 'PATHL7'
Lab_Type_OSCAR_To_OSCAR = 'OSCAR_TO_OSCAR_HL7_V2'
Lab_Type_IHA = 'IHA'

# The upload protocol's primitives, as the server implements them
RSA_Key_Size = 2048
AES_Key_Size = 16
AES_Block_Size = 128

# The name under which the server keeps its own key pair
Server_Key_Name = 'oscar'

# ################################################################################################################################
# ################################################################################################################################

class OSCAR(LiveSystem):
    """ OSCAR EMR - lab results in through the signed upload the production uploaders use, an ADT^A04 out
    for every patient created.
    """

    name = 'oscar'
    block_number = 6
    purposes = ('web', 'mariadb')
    password_rules = PasswordRules(8, True, True, True, True)
    images = {
        'db':    'mariadb:10.5',
        'oscar': 'openosp/open-osp:2026.09.17',
    }
    directory = os.path.dirname(__file__)
    summary = 'OSCAR EMR on MariaDB, lab results in through newLabUpload, ADT^A04 out on demographic creation.'
    ui_purpose = 'web'
    ui_path = Context_Path + '/'
    ui_username = Default_Username + ', PIN ' + Default_PIN

# ################################################################################################################################

    def environment(self, ports:'strintdict', password:'str') -> 'strstrdict':
        out = super().environment(ports, password)
        out['OSCAR_CONFIG_DIR'] = work_directory(Config_Dir_Name)
        out['OSCAR_SCRIPTS_DIR'] = work_directory(Scripts_Dir_Name)

        return out

# ################################################################################################################################

    def prepare(self, handle:'Handle') -> 'None':
        """ Renders the properties files with our database password and the A04 target, and takes the database
        scripts out of the image so the database container can run them.
        """
        _render_properties(handle.password)
        _extract_database_scripts(handle)

# ################################################################################################################################

    def after_start(self, handle:'Handle') -> 'None':
        """ Creates and fills the database once the server accepts connections - the webapp cannot do that itself.
        """
        check = partial(_is_database_up, handle)
        wait_until(check, 'oscar database')

        if _has_database(handle):
            return

        script = f'cd {DB_Scripts_Dir} && sh {Create_Database_Script} {Database_User} "{handle.password}" {Database_Name}'
        _ = handle.stack.exec(DB_Service, ['sh', '-c', script])

        # The scripts create the account with an expiry and a forced reset - the reset is what we want, the expiry is not
        sql = f"update security set date_ExpireDate=DATE_ADD(CURDATE(), INTERVAL 360 MONTH), b_ExpireSet=1 where user_name='{Default_Username}'"
        _ = query(handle, sql)

# ################################################################################################################################

    def is_ready(self, handle:'Handle') -> 'bool':
        """ True once the login page is served.
        """
        url = handle.http_url('web') + Login_Page
        result = request('GET', url)

        if result.status != OK:
            return False

        out = b'name="username"' in result.body
        return out

# ################################################################################################################################

    def after_ready(self, handle:'Handle') -> 'None':
        """ Completes the forced first-login password change and installs the upload key pair.
        """
        _complete_first_login(handle)
        install_server_keys(handle)

# ################################################################################################################################
# ################################################################################################################################

def a04_port() -> 'int':
    """ The port OSCAR sends its ADT^A04 messages to on the host.
    """
    if value := os.environ.get(A04_Port_Env):
        out = int(value)
    else:
        out = A04_Default_Port

    return out

# ################################################################################################################################

def _render_properties(password:'str') -> 'None':
    source = fetch_once(Properties_URL, Properties_Cache_Name)
    config_dir = work_directory(Config_Dir_Name)

    with open(source, encoding='utf8') as f:
        lines = f.read().splitlines()

    out:'strlist' = []

    for line in lines:
        if line.startswith('db_username'):
            out.append(f'db_username = {Database_User}')
        elif line.startswith('db_password'):
            continue
        elif line.startswith('HL7_A04_TRANSPORT_ADDR'):
            out.append(f'HL7_A04_TRANSPORT_ADDR={A04_Host}')
        elif line.startswith('HL7_A04_TRANSPORT_PORT'):
            out.append(f'HL7_A04_TRANSPORT_PORT={a04_port()}')
        else:
            out.append(line)

    out.append(f'db_password = {password}')

    with open(os.path.join(config_dir, 'oscar.properties'), 'w', encoding='utf8') as f:
        _ = f.write('\n'.join(out) + '\n')

    source = fetch_once(Drugref_URL, Drugref_Cache_Name)

    with open(source, encoding='utf8') as f:
        lines = f.read().splitlines()

    out = []

    for line in lines:
        if line.startswith('db_password'):
            out.append(f'db_password={password}')
        else:
            out.append(line)

    with open(os.path.join(config_dir, 'drugref2.properties'), 'w', encoding='utf8') as f:
        _ = f.write('\n'.join(out) + '\n')

# ################################################################################################################################

def _extract_database_scripts(handle:'Handle') -> 'None':
    """ The scripts sit in the webapp image - a one-off container tars them up and they land in the mounted directory.
    """
    scripts_dir = work_directory(Scripts_Dir_Name)
    marker = os.path.join(scripts_dir, Create_Database_Script)

    if os.path.exists(marker):
        return

    data = handle.stack.run_raw(Webapp_Service, ['tar', '-C', Image_Scripts_Dir, '-cf', '-', '.'])

    with tarfile.open(fileobj=BytesIO(data)) as archive:
        archive.extractall(scripts_dir, filter='data')

# ################################################################################################################################

def _mysql_arguments(handle:'Handle', *arguments:'str') -> 'strlist':
    out = ['mysql', f'-u{Database_User}', f'-p{handle.password}']
    out.extend(arguments)

    return out

# ################################################################################################################################

def _is_database_up(handle:'Handle') -> 'bool':
    arguments = ['mysqladmin', f'-u{Database_User}', f'-p{handle.password}', 'ping', '--silent']
    _ = handle.stack.exec(DB_Service, arguments)

    return True

# ################################################################################################################################

def _has_database(handle:'Handle') -> 'bool':
    output = handle.stack.exec(DB_Service, _mysql_arguments(handle, '-N', '-B', '-e', f"show databases like '{Database_Name}'"))

    out = output.strip() == Database_Name
    return out

# ################################################################################################################################

def query(handle:'Handle', sql:'str') -> 'anylist':
    """ Runs one statement against the OSCAR database and returns its rows as lists of strings.
    """
    arguments = _mysql_arguments(handle, '-N', '-B', Database_Name)
    output = handle.stack.exec(DB_Service, arguments, input_data=sql.encode('utf8'))

    out:'anylist' = []

    for line in output.splitlines():
        if line:
            out.append(line.split('\t'))

    return out

# ################################################################################################################################

def _complete_first_login(handle:'Handle') -> 'None':
    """ The first login is answered with a forced password change - this completes it with our password.
    A restart already has it and the first step simply logs in.
    """
    session = Session(handle.http_url('web'))
    fields:'strstrdict' = {
        'username': Default_Username,
        'password': Default_Initial_Password,
        'pin': Default_PIN,
        'submit': 'Sign In',
    }

    result = session.post_form(Login_Action, fields)

    if b'forcedpasswordchange' not in result.body:
        return

    fields = {
        'forcedpasswordchange': 'true',
        'oldPassword': Default_Initial_Password,
        'newPassword': handle.password,
        'confirmPassword': handle.password,
    }

    result = session.post_form(Login_Action, fields)
    expect_status(result, OK, 'first-login password change')

    if b'errormsg' in result.body:
        raise Exception('OSCAR did not accept the new password')

# ################################################################################################################################

def login(handle:'Handle') -> 'Session':
    """ A browser session logged in as the default provider with our password.
    """
    out = Session(handle.http_url('web'))
    fields:'strstrdict' = {
        'username': Default_Username,
        'password': handle.password,
        'pin': Default_PIN,
        'submit': 'Sign In',
    }

    result = out.post_form(Login_Action, fields)
    expect_status(result, OK, 'login')

    if b'loginfailed' in result.body or b'name="username"' in result.body:
        raise Exception('OSCAR login failed')

    return out

# ################################################################################################################################
# ################################################################################################################################

def _new_rsa_key() -> 'rsa.RSAPrivateKey':
    out = rsa.generate_private_key(public_exponent=65537, key_size=RSA_Key_Size)
    return out

# ################################################################################################################################

def _public_base64(key:'rsa.RSAPrivateKey') -> 'str':
    der = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    out = b64encode(der).decode('ascii')
    return out

# ################################################################################################################################

def _private_base64(key:'rsa.RSAPrivateKey') -> 'str':
    der = key.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    out = b64encode(der).decode('ascii')
    return out

# ################################################################################################################################

def _server_key_path() -> 'str':
    out = os.path.join(work_directory(Config_Dir_Name), 'server-key.pem')
    return out

# ################################################################################################################################

def _client_key_path(service:'str') -> 'str':
    out = os.path.join(work_directory(Config_Dir_Name), f'client-key-{service}.pem')
    return out

# ################################################################################################################################

def _load_key(path:'str') -> 'rsa.RSAPrivateKey':
    with open(path, 'rb') as f:
        data = f.read()

    out = serialization.load_pem_private_key(data, password=None)

    if not isinstance(out, rsa.RSAPrivateKey):
        raise Exception(f'Not an RSA key under {path}')

    return out

# ################################################################################################################################

def _save_key(path:'str', key:'rsa.RSAPrivateKey') -> 'None':
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    with open(path, 'wb') as f:
        _ = f.write(pem)

# ################################################################################################################################

def install_server_keys(handle:'Handle') -> 'None':
    """ The key pair the server decrypts uploads with - what Administration generates, written straight to its table.
    """
    path = _server_key_path()

    if os.path.exists(path):
        key = _load_key(path)
    else:
        key = _new_rsa_key()
        _save_key(path, key)

    sql = (
        f"replace into oscarKeys (name, pubKey, privKey) "
        f"values ('{Server_Key_Name}', '{_public_base64(key)}', '{_private_base64(key)}')"
    )

    _ = query(handle, sql)

# ################################################################################################################################

def add_upload_service(handle:'Handle', service:'str', lab_type:'str') -> 'None':
    """ A laboratory allowed to upload, with the handler its messages go through - the client key pair is ours,
    the server gets the public half.
    """
    path = _client_key_path(service)

    if os.path.exists(path):
        key = _load_key(path)
    else:
        key = _new_rsa_key()
        _save_key(path, key)

    sql = (
        f"replace into publicKeys (service, type, pubKey, privateKey) "
        f"values ('{service}', '{lab_type}', '{_public_base64(key)}', '{_private_base64(key)}')"
    )

    _ = query(handle, sql)

# ################################################################################################################################

def _server_public_key(handle:'Handle') -> 'rsa.RSAPublicKey':
    key = _load_key(_server_key_path())

    out = key.public_key()
    return out

# ################################################################################################################################

def _pad(data:'bytes') -> 'bytes':
    """ PKCS#5 padding, what Java's plain `AES` cipher applies.
    """
    padder = PKCS7(AES_Block_Size).padder()

    out = padder.update(data) + padder.finalize()
    return out

# ################################################################################################################################

def upload_lab(handle:'Handle', session:'Session', service:'str', message:'bytes') -> 'str':
    """ Uploads one HL7 message the way the production uploaders do - AES-encrypted under a fresh key,
    that key RSA-encrypted for the server, the plaintext signed with the service's key. Returns the outcome
    the server names in its status line.
    """
    server_public = _server_public_key(handle)
    client_key = _load_key(_client_key_path(service))

    aes_key = token_bytes(AES_Key_Size)
    cipher = Cipher(algorithms.AES(aes_key), modes.ECB())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(_pad(message)) + encryptor.finalize()

    wrapped_key = server_public.encrypt(aes_key, padding.PKCS1v15())
    signature = client_key.sign(message, padding.PKCS1v15(), hashes.MD5())

    fields:'strstrdict' = {
        'key': b64encode(wrapped_key).decode('ascii'),
        'signature': b64encode(signature).decode('ascii'),
        'service': service,
        'use_http_response_code': '1',
    }

    files = [FileField('importFile', f'{service}.hl7', encrypted, 'application/octet-stream')]

    result = session.post_multipart(Lab_Upload_Action, fields, files)

    out = result.body.decode('utf8', 'replace').strip()

    if result.status != OK:
        raise Exception(f'Lab upload failed with {result.status}: {out}')

    return out

# ################################################################################################################################

def filed_labs(handle:'Handle', accession:'str') -> 'anylist':
    """ What OSCAR filed for one accession number - lab number, patient name, report status and routing.
    """
    sql = (
        "select i.lab_no, i.last_name, i.first_name, i.report_status, i.result_status, r.provider_no, r.status "
        "from hl7TextInfo i left join providerLabRouting r on r.lab_no = i.lab_no "
        f"where i.accessionNum = '{accession}'"
    )

    out = query(handle, sql)
    return out

# ################################################################################################################################

def lab_message(handle:'Handle', lab_no:'str') -> 'str':
    """ The message text OSCAR stored for one lab.
    """
    rows = query(handle, f'select message from hl7TextMessage where lab_id = {lab_no}')

    if not rows:
        raise Exception(f'No lab message under {lab_no}')

    out = rows[0][0]
    return out

# ################################################################################################################################
# ################################################################################################################################
