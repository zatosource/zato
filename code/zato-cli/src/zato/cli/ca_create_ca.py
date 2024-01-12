# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, uuid, tempfile

# Zato
from zato.cli import ca_defaults, default_ca_name, ZatoCommand
from zato.common.util.open_ import open_w

openssl_template = """
dir                            = {target_dir}

[ ca ]
default_ca                     = CA_default

[ CA_default ]
serial                         = {ca_serial}
database                       = {ca_certindex}
new_certs_dir                  = {target_dir_rel}
certificate                    = {ca_key}
private_key                    = {private_key}
default_days                   = 3650
default_md                     = sha1
preserve                       = no
email_in_dn                    = no
nameopt                        = default_ca
certopt                        = default_ca
policy                         = policy_match

[ policy_match ]
countryName                    = match
stateOrProvinceName            = match
organizationName               = match
organizationalUnitName         = supplied
commonName                     = supplied

[ req ]
default_bits                   = 2048
default_md                     = sha1
string_mask                    = nombstr
distinguished_name             = req_distinguished_name

[ req_distinguished_name ]
0.organizationName             = Organization Name (company)
organizationalUnitName         = Organization Unit Name (department, division)
localityName                   = Locality Name (city, district)
stateOrProvinceName            = State or Province Name (full name)
countryName                    = Country Name (2 letter code)
countryName_min                = 2
countryName_max                = 2
commonName                     = Common Name (hostname, IP, or your name)
commonName_max                 = 64

0.organizationName_default     = {organization}
organizationalUnitName_default = {organizational_unit}
localityName_default           = {locality}
stateOrProvinceName_default    = {state_or_province}
countryName_default            = {country}
commonName_default             = {common_name}

[ v3_ca ]
basicConstraints               = CA:TRUE
subjectKeyIdentifier           = hash
authorityKeyIdentifier         = keyid:always,issuer:always

[ v3_server ]
basicConstraints               = CA:FALSE
subjectKeyIdentifier           = hash
extendedKeyUsage               = serverAuth

[ v3_client_server ]
basicConstraints               = CA:FALSE
subjectKeyIdentifier           = hash
extendedKeyUsage               = serverAuth,clientAuth
"""

class Create(ZatoCommand):
    """Creates a new certificate authority
    """
    opts = [
        {'name':'--organization', 'help':'CA organization name (defaults to {organization})'.format(**ca_defaults)},
        {'name':'--organizational-unit',
            'help':'CA organizational unit name (defaults to {default})'.format(default=default_ca_name)},
        {'name':'--locality', 'help':'CA locality name (defaults to {locality})'.format(**ca_defaults)},
        {'name':'--state-or-province',
            'help':'CA state or province name (defaults to {state_or_province})'.format(**ca_defaults)},
        {'name':'--country', 'help':'CA country (defaults to {country})'.format(**ca_defaults)},
        {'name':'--common-name', 'help':'CA common name (defaults to {default})'.format(default=default_ca_name)},
    ]

    needs_empty_dir = True

    def __init__(self, args):
        super(Create, self).__init__(args)
        self.target_dir = os.path.abspath(args.path)

    def execute(self, args, show_output=True):
        self.logger.info('Create CA execute')
        # Prepare the directory layout
        os.mkdir(os.path.join(self.target_dir, 'ca-material'))
        open_w(os.path.join(self.target_dir, 'ca-material', 'ca-serial')).write('01')
        open_w(os.path.join(self.target_dir, 'ca-material', 'ca-password')).write(uuid.uuid4().hex)
        open_w(os.path.join(self.target_dir, 'ca-material', 'ca-certindex'))
        open_w(os.path.join(self.target_dir, 'ca-material', 'ca-certindex.attr')).write('unique_subject = no')
        open_w(os.path.join(self.target_dir, 'ca-material', 'openssl-template.conf')).write(openssl_template)

        # Create the CA's cert and the private key

        template_args = {}
        for name in('organization', 'organizational_unit', 'locality', 'state_or_province', 'country'):
            value = self._get_arg(args, name, ca_defaults[name])
            template_args[name] = value

        template_args['common_name'] = self._get_arg(args, 'common_name', default_ca_name)
        template_args['target_dir'] = self.target_dir
        template_args['ca_serial'] = '$dir/ca-material/ca-serial'
        template_args['ca_certindex'] = '$dir/ca-material/ca-certindex'
        template_args['target_dir_rel'] = '$dir'
        template_args['ca_key'] = '$dir/ca-material/ca-cert.pem'
        template_args['private_key'] = '$dir/ca-material/ca-key.pem'

        import platform
        system = platform.system()
        is_windows = 'windows' in system.lower()

        if is_windows:
            template_args['target_dir'] = self.target_dir.replace('\\','/')
            template_args['ca_serial'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-serial')).replace('\\','/')
            template_args['ca_certindex'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-certindex')).replace('\\','/')
            template_args['target_dir_rel'] = os.path.relpath(self.target_dir).replace('\\','/')
            template_args['ca_key'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-cert.pem')).replace('\\','/')
            template_args['private_key'] = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-key.pem')).replace('\\','/')

        f = tempfile.NamedTemporaryFile(mode='w+')
        f.write(openssl_template.format(**template_args))
        f.flush()

        ca_key = os.path.join(self.target_dir, 'ca-material', 'ca-key.pem')
        ca_cert = os.path.join(self.target_dir, 'ca-material', 'ca-cert.pem')
        ca_password = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-password'))

        if is_windows:
            ca_key = os.path.join(self.target_dir, 'ca-material', 'ca-key.pem').replace('\\','\\\\')
            ca_cert = os.path.join(self.target_dir, 'ca-material', 'ca-cert.pem').replace('\\','\\\\')
            ca_password = os.path.relpath(os.path.join(self.target_dir, 'ca-material', 'ca-password')).replace('\\','\\\\')

        cmd = """openssl req -batch -new -x509 -newkey rsa:2048 -extensions v3_ca -keyout \
                   {ca_key} -out {ca_cert} -days 3650 \
                   -config {config} -passout file:{ca_password}""".format(
                       config=f.name,
                       ca_key=ca_key,
                       ca_cert=ca_cert,
                       ca_password=ca_password
                       )
        os.system(cmd)
        f.close()

        for name in('csr', 'cert', 'priv', 'pub'):
            os.mkdir(os.path.join(self.target_dir, 'out-{}'.format(name)))

        # Mark the directory being a Zato CA one.
        open_w(os.path.join(self.target_dir, '.zato-ca-dir'))

        # Initial info
        self.store_initial_info(self.target_dir, self.COMPONENTS.CA.code)

        if show_output:
            if self.verbose:
                msg = 'Successfully created a certificate authority in {path}'.format(
                    path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))
                self.logger.debug(msg)
            else:
                self.logger.info('OK')
