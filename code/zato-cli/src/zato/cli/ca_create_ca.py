# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, uuid, tempfile

# Zato
from zato.cli import ca_defaults, default_ca_name, ZatoCommand

openssl_template = '''
dir                            = {target_dir}

[ ca ]
default_ca                     = CA_default

[ CA_default ]
serial                         = $dir/ca-material/ca-serial
database                       = $dir/ca-material/ca-certindex
new_certs_dir                  = $dir
certificate                    = $dir/ca-material/ca-cert.pem
private_key                    = $dir/ca-material/ca-key.pem
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
default_bits                   = 4096
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
'''

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

        # Prepare the directory layout
        os.mkdir(os.path.join(self.target_dir, 'ca-material'))
        open(os.path.join(self.target_dir, 'ca-material/ca-serial'), 'w').write('01')
        open(os.path.join(self.target_dir, 'ca-material/ca-password'), 'w').write(uuid.uuid4().hex)
        open(os.path.join(self.target_dir, 'ca-material/ca-certindex'), 'w')
        open(os.path.join(self.target_dir, 'ca-material/ca-certindex.attr'), 'w').write('unique_subject = no')
        open(os.path.join(self.target_dir, 'ca-material/openssl-template.conf'), 'w').write(openssl_template)

        # Create the CA's cert and the private key

        template_args = {}
        for name in('organization', 'organizational_unit', 'locality', 'state_or_province', 'country'):
            value = self._get_arg(args, name, ca_defaults[name])
            template_args[name] = value

        template_args['common_name'] = self._get_arg(args, 'common_name', default_ca_name)
        template_args['target_dir'] = self.target_dir

        f = tempfile.NamedTemporaryFile(mode='w+')
        f.write(openssl_template.format(**template_args))
        f.flush()

        cmd = """openssl req -batch -new -x509 -newkey rsa:4096 -extensions v3_ca -keyout \
                   {target_dir}/ca-material/ca-key.pem -out {target_dir}/ca-material/ca-cert.pem -days 3650 \
                   -config {config} -passout file:{target_dir}/ca-material/ca-password >/dev/null 2>&1""".format(
                       config=f.name, target_dir=self.target_dir)
        os.system(cmd)
        f.close()

        for name in('csr', 'cert', 'priv', 'pub'):
            os.mkdir(os.path.join(self.target_dir, 'out-{}'.format(name)))

        # Mark the directory being a Zato CA one.
        open(os.path.join(self.target_dir, '.zato-ca-dir'), 'w')

        # Initial info
        self.store_initial_info(self.target_dir, self.COMPONENTS.CA.code)

        if show_output:
            if self.verbose:
                msg = 'Successfully created a certificate authority in {path}'.format(
                    path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))
                self.logger.debug(msg)
            else:
                self.logger.info('OK')
