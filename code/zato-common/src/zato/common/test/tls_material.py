# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# # ##############################################################################################################################
#
# ** WARNING ** WARNING ** WARNING **
#
# Crypto material below is not safe for use outside of Zato's own unittests. Don't use it anywhere else.
#
# # ##############################################################################################################################

ca_key = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
""".strip()

ca_cert = """
-----BEGIN CERTIFICATE-----
MIIFoDCCA4igAwIBAgIJAMpUuR9ijhIRMA0GCSqGSIb3DQEBBQUAMBsxCzAJBgNV
BAYTAkFVMQwwCgYDVQQDEwNDQTIwHhcNMTQwNzIwMTgyMTU2WhcNMjQwNzE3MTgy
MTU2WjAbMQswCQYDVQQGEwJBVTEMMAoGA1UEAxMDQ0EyMIICIjANBgkqhkiG9w0B
AQEFAAOCAg8AMIICCgKCAgEAnMEaU26+UqOtQkiDkCiJdfB/Pv4sL7yef3iE9Taf
bpuTPdheqzkeR9NHxklyjKMjrAlVrIDu1D4ZboIDmgcq1Go4OCWhTwriFrATJYlp
LZhOlzd5/hC0SCJ1HljR4/mOWsVj/KanftMYzSNADjQ0cxVtPguj/H8Y7CDlQxQ4
d6I1+JPGCUIwG3HfSwC5Lxqp/QLUC6OuKqatwDetaE7+t9Ei6LXrFvOg6rPb4cuQ
jymzWnql0Q1NEOGyifbhXaQgO6mM5DaT/q3XtakqviUZDLbIo4IWJAmvlB8tbcbP
wzku+6jEBhkdTAzAb6K6evTK4wUUSrHTE6vF/PHq5+KLrGReX/NrCgdTH/LB/Aux
817IF2St4ohiI8XVtWoC/Ye94c1ju/LBWIFPZAxFoNJJ5zvlLwJN8/o1wuIVNQ3p
4FWTXVArmSOGEmQL48UTUFq/VKJeoDstUoyIsKnBn4uRMcYPIsMh1VF6Heayq1T9
eO2Uwkw75IZVLVA9WaXnCIc07peDREFbyWtyKzpDa2Bh8bLVQ/tyB+sBJkO2lGPb
PMRZl50IhdD7JENNfTG89LCBNioPDNQXN9q3XQYSZgQ9H70Zp+Y3/ipXvIAelPwq
Uyg7YoIjOTqFF25g2c/XSrwSpKCr22lb1vkCLUT7pA0tslMVdULo1FkkkfIDDiHs
FC8CAwEAAaOB5jCB4zAdBgNVHQ4EFgQUmh+yIUO2PG/fMMMjXjestsQPg48wSwYD
VR0jBEQwQoAUmh+yIUO2PG/fMMMjXjestsQPg4+hH6QdMBsxCzAJBgNVBAYTAkFV
MQwwCgYDVQQDEwNDQTKCCQDKVLkfYo4SETAPBgNVHRMBAf8EBTADAQH/MBEGCWCG
SAGG+EIBAQQEAwIBBjAJBgNVHRIEAjAAMCsGCWCGSAGG+EIBDQQeFhxUaW55Q0Eg
R2VuZXJhdGVkIENlcnRpZmljYXRlMAkGA1UdEQQCMAAwDgYDVR0PAQH/BAQDAgEG
MA0GCSqGSIb3DQEBBQUAA4ICAQBJsjzUBFUOpuOGz3n2MwcH8IaDtHyKNTsvhuT8
rS2zVpnexUdRgMzdG0K0mgfKLc+t/oEt8oe08ZtRnpj1FVJLvz68cPbEBxsqkTWi
Kf65vtTtoZidVBnpIC4Tq7Kx0XQXg8h+3iykqFF6ObqxZix/V9hs3QDRnTNiWGE7
thGCAWWVy1r56nkS91uhQhSWt471FevmdxOdf7+4Df8OsQGcPF6sH/TQcOVgDc20
EiapNMpRxQmhyOI7HBZdYGmHM6okGTf/mtUFhBLKDfdLfBHoGhUINiv939O6M6X3
LFserZ9DEd9IIOTsvYQyWhJDijekEtvBfehwp1NjQcity/l/pwUajw/NUok56Dj7
jHBjHJSSgb5xJ9EMrtJ2Qm2a5pUZXwF2cJIxBjQR5bufJpgiYPRjzxbncStuibps
JjSGwiGvoyGbg2xLw7sSI7C2G9KGMtwbS4Di1/e0M1WfFg/ibT3Z1VhqtEL6Yr+m
CG6rI1BBiPfJqqeryLg8q9a4CQFA+vhXSzvly/pT7jZcLyXc/6pCU6GqjFZDaiGI
sBQseOvrJQ1CouAMnwc9Z8vxOOThqtMTZsGGawi+16+5NmpLwW53V/wtHUZuk39F
29ICmBRa3wrCyhNMb+AFhaPjO34jtRGqeOJA98eS29GooycDnh/Uwi3txZu6DNmZ
NVRV1A==
-----END CERTIFICATE-----
""".strip()

ca_cert_invalid = """
-----BEGIN CERTIFICATE-----
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
wSQh3r/cB+X3alAbvPwTlzyNXFu1
-----END CERTIFICATE-----
""".strip()

client1_key = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
""".strip()

client1_cert = """
-----BEGIN CERTIFICATE-----
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
svkkFA==
-----END CERTIFICATE-----

""".strip()


server1_key = """
-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----

""".strip()

server1_cert = """
-----BEGIN CERTIFICATE-----
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
-----END CERTIFICATE-----
""".strip()
