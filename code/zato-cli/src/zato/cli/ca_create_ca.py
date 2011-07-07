# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, uuid, tempfile

# Zato
from zato.cli import ZatoCommand, ca_defaults, default_ca_name

openssl_template = """
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
default_md                     = md5
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
default_md                     = md5
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

class CreateCA(ZatoCommand):
    command_name = "ca create-ca"

    opts = [
        dict(name="--organization", help="CA organization name (defaults to {organization})".format(**ca_defaults)),
        dict(name="--organizational-unit", help="CA organizational unit name (defaults to {default})".format(default=default_ca_name)),
        dict(name="--locality", help="CA locality name (defaults to {locality})".format(**ca_defaults)),
        dict(name="--state-or-province", help="CA state or province name (defaults to {state_or_province})".format(**ca_defaults)),
        dict(name="--country", help="CA country (defaults to {country})".format(**ca_defaults)),
        dict(name="--common-name", help="CA common name (defaults to {default})".format(default=default_ca_name)),
    ]

    needs_empty_dir = True

    def __init__(self, target_dir):
        super(CreateCA, self).__init__()
        self.target_dir = os.path.abspath(target_dir)

    description = "Creates a Certificate Authority."

    def execute(self, args):

        # Prepare the directory layout
        os.mkdir(os.path.join(self.target_dir, "ca-material"))
        open(os.path.join(self.target_dir, "ca-material/ca-serial"), "w").write("01")
        open(os.path.join(self.target_dir, "ca-material/ca-password"), "w").write(uuid.uuid4().hex)
        open(os.path.join(self.target_dir, "ca-material/ca-certindex"), "w")
        open(os.path.join(self.target_dir, "ca-material/ca-certindex.attr"), "w").write("unique_subject = no")
        open(os.path.join(self.target_dir, "ca-material/openssl-template.conf"), "w").write(openssl_template)

        # Create the CA's cert and the private key

        template_args = {}

        common_name = self._get_arg(args, "common_name", default_ca_name)
        organization = self._get_arg(args, "organization", ca_defaults["organization"])
        organizational_unit = self._get_arg(args, "organizational_unit", default_ca_name)
        locality = self._get_arg(args, "locality", ca_defaults["locality"])
        state_or_province = self._get_arg(args, "state_or_province", ca_defaults["state_or_province"])
        country = self._get_arg(args, "country", ca_defaults["country"])

        template_args["common_name"] = common_name
        template_args["organization"] = organization
        template_args["organizational_unit"] = organizational_unit
        template_args["locality"] = locality
        template_args["state_or_province"] = state_or_province
        template_args["country"] = country

        template_args["target_dir"] = self.target_dir

        f = tempfile.NamedTemporaryFile()
        f.write(openssl_template.format(**template_args))
        f.flush()

        cmd = """openssl req -batch -new -x509 -newkey rsa:2048 -extensions v3_ca -keyout \
                   {target_dir}/ca-material/ca-key.pem -out {target_dir}/ca-material/ca-cert.pem -days 3650 \
                   -config {config} -passout file:{target_dir}/ca-material/ca-password""".format(config=f.name,
                                                                    target_dir=self.target_dir)
        os.system(cmd)
        f.close()

        os.mkdir(os.path.join(self.target_dir, "out-csr"))
        os.mkdir(os.path.join(self.target_dir, "out-cert"))
        os.mkdir(os.path.join(self.target_dir, "out-priv"))
        os.mkdir(os.path.join(self.target_dir, "out-pub"))

        # Mark the directory being a Zato CA one.
        open(os.path.join(self.target_dir, ".zato-ca-dir"), "w")

        msg = "\nSuccessfully created a Certificate Authority in {path}".format(
            path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))

        print(msg)

def main(target_dir):
    CreateCA(target_dir).run()

if __name__ == "__main__":
    main(".")