# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

# Bunch
from bunch import Bunch

# lxml
from lxml import etree

# Zato
from zato.common.util import api as util_api, StaticConfig
from zato.common.util.search import SearchResults
from zato.common.py23_ import maxint
from zato.common.test.tls_material import ca_cert

# ################################################################################################################################
# ################################################################################################################################

class UtilsTestCase(TestCase):
    def test_uncamelify(self):
        original = 'ILikeToReadWSDLDocsNotReallyNOPENotMeQ'
        expected1 = 'i-like-to-read-wsdl-docs-not-really-nope-not-me-q'
        self.assertEqual(util_api.uncamelify(original), expected1)

# ################################################################################################################################
# ################################################################################################################################

class XPathTestCase(TestCase):
    def test_validate_xpath(self):
        self.assertRaises(etree.XPathSyntaxError, util_api.validate_xpath, 'a b c')
        self.assertTrue(util_api.validate_xpath('//node'))

# ################################################################################################################################
# ################################################################################################################################

class TLSTestCase(TestCase):
    def test_validate_tls_cert_from_payload(self):
        info = util_api.get_tls_from_payload(ca_cert)
        self.assertEqual(info, 'C=AU; CN=CA2')

    def test_replace_private_key(self):
        self.maxDiff = maxint
        payload = '{"value": "-----BEGIN RSA PRIVATE KEY-----\\r\\nMIIJKQIBAAKCAgEA0nRSiWO6a68MQNxRcgUgDwHSB6ldSCAr6Xl9otadBN02fN6V\\r\\nZdFU4M5Gv+IEFpkgngStGHFyfAjX2pXXiL4Zpvggbzbiyg42y3s6vnE2I33NtEUd\\r\\nn3W5XiHBTUjzh7oETfK5lW1TnYXFBPBMSUjBzyQ1IUq9YZp3+HGLfB08ijsz7azZ\\r\\n35IvlTT12GbS09+85+Mtik+ABEtSiUbBpgZv\\/W0qNj35Rky1Q\\/U236QJOjPQzG8p\\r\\nE12ep1AQECsSWAv3VpQoLHQFLMrLsfHNKAkTFpE0p3z3vjtc9P\\/ihxf+b5bA0R4s\\r\\nmbfnG1HNauLs73Y6P2K7PRa+LoQe5C4ljJ6KFNakRYkieSs5Ic4kRZxdr5BgamuH\\r\\n5nXYbKmDs9wFYE3s4CpHpEJip377utnodXU2W3F67uS4GS6nmBDa07xPJD\\/2NV9E\\r\\n3xTXTJXhxDdqnheIhm5u1rXPbqqp6F12mSFanTgNEd2Fa17o8lzvwJ6xfVr9rm1a\\r\\nxROA1gv0SEJFV9pCMB3U3X9L3Kf+xqzO\\/kxQOx3dyEFYYvfSuVm1CW\\/VWcuDXiFv\\r\\nYdgjubNOkYjqjzrYq\\/4Ef47NekLBidD+K\\/+\\/YjnQ55e4KDe780iI8euuFANTM471\\r\\n6FzU0kqelo360mb5h16CIqVBmCDXTcntqtpnlq2Xu2fsz3AdyyFNvWyk2GECAwEA\\r\\nAQKCAgBzE+A9+CZr06Ajp1Vxv5O0IQ6z2cyEL\\/NTC3fDnw7lJgExbpTKxBhhhOny\\r\\n6qfJo5nOTkhIYWB0qnE9uUnOIATu5Cb4KU8BpZwY0B1jHYy5A4WD2XdFRp5B9rs4\\r\\ng3eG9BR+ewc3yjw6mncNKEjOmdZAalATEEdWI50OYSggiewcuhq\\/EBFiyxDxya\\/U\\r\\n0QTfjixBsFuqkaYysu1C20nwevyp2xOF7YVtB2zm6CNFTvEsvkCiSPZw\\/HRQkNr3\\r\\nvFWfh4uL8B+3jwl1YL7ZYpsIFU42vNfJ7e+aOeOupG096cTbR9fPgWxp8cGRkr18\\r\\ngPGGT2OyXU59LP55eQ1bQFCP\\/\\/EITdxPaIgviD9tAiEdwhWTKzKCPDLNw83d9baX\\r\\nMI\\/b4vRCLdnN3c7bhrffdJWRT\\/5\\/yCcqdZrgPQkLrv2r6klbhyrFVKeDWJYusNKu\\r\\ntcYFoq8qZO0nzW5OKpMvBgdxUh\\/PrpBCDKB\\/YxpxL5Vvc2TY1yLFZyx2YaJVpupe\\r\\nEdxCgdjh1SMjQjPb9g5vlVX13EOdY8PXWZoYDe0qB\\/DY7NPeUEIADhIsGTR0KHZK\\r\\nnk77h4Qn3d91GcZaqyhor8y5x3TTA+QDRImFfOkhI+PRobjb3XLDRK34jETXuW0u\\r\\nyOL2ULLKFDW\\/uBSBQ+3Gc+VINx06wuRIQOAgw8P07QRMR7+Q8QKCAQEA9AlYhXEv\\r\\nvjiRXxETZEpzVuSSQNp82bzfXEBYGG9Mt9pdWpR24obgWehsrXUZDAEyZYSu66SQ\\r\\nyhd0WStzo+b0fLY5vF1OLetYMuHkSSRttB6IIfO0aZqj3o4f8H\\/2JBz0XpNJKV1B\\r\\nbzPZ5DTVZ2qXUBU9RxpOzpET1kv1RzN8Is78L8bE4HYNcgySkoQaXxQG8\\/soq2Rs\\r\\ndbI1FzTEVWNvj+vIfDaF0r70lQgAoNqYqIL6pnnqM12hq8SH8WI7Ao2a30UQgEEO\\r\\nrnle76oyZZfILt0V2GUu31hLjDPEy8sgQCtnGOKh6C2XMZw\\/krfelRrU1V0XAzun\\r\\n9zeD+woOg2sCjwKCAQEA3MWFgto72Yk6RTKvqtXnuVCLKtdnOC9QIGWkPDwtdGkO\\r\\nLukgzew6NBwl4VIWKdSbue6EHi9oj7OYcc949J9Z6BDyEWWF3xwi+G9Y\\/4csAult\\r\\nrpSz+y6feM3KlrF9oYltMoPAjbwCP8KqncXQCRkmIrah8OPBO+4xLzpj+yOLF7GV\\r\\nYizlk5yWa1W+63nuDgc+QUAgN+dSNECigyxlsenR+Nbup6KR7nkMWSaDCyP7GN3E\\r\\n\\/J8qG5rno0gwMQIVl4HiYVNMCywpooeog3fPvj87eAD0e+SNwUi4edw7Azz9IkEB\\r\\nN+\\/iQC1IVuCvgef1usnQnepEkwmNZhBOZoUcH3YuDwKCAQEArsTur4qTDaEHg1UA\\r\\nVUf4eFdz4pxW470fHbs7HCzBfb4WM2O2DJ9ZlyocgtEk4fMNe6TdfQc7ZnALtDyp\\r\\nMc2adKIwkRUlgz9TyAT87+D17BQdnGsjXqoQB7gzaZLK3awa2oySzdvqm9A\\/kO7B\\r\\nkrHEsea0HvLZU5iU41k8zQQzN96Sv0iUAMiq8m3Mnr+a\\/1KhdCQASVa\\/Uj8RRJBW\\r\\nt2xiHmlXCJYnmvmEwiKcCJbk03ISPh17u9OnkBNM5HNcHYT6UEHvAlsVP6DOe8eh\\r\\nFh7wj5doKLS2L9\\/VIxCENQtBCpPK3wiXuWbFLBNheBrUfmZb3H4xl\\/AmZ6dLjwLx\\r\\nx+5gQwKCAQBAvEZ+7SEZk4ybl9Y84MY257A3GrxwlCcJqOQ0qWymsttu0\\/tDhp42\\r\\ng350CI7pKyeSqKbi9wHRCVeNH8oW6NcDHlzszvknR+fVM0lEfE1ieTIpO\\/9eivhG\\r\\nAwoBkAAHqvVzF4ERzmxWZ+2Bn+x1joNJMIZhzVbvDNQtRhDlJjH1+6OTCxkyZHsS\\r\\n9Cysfa9ZO7R8i6Im4lSPb9h3YEBdn\\/Nq5RNL4naqF6KQTaOlU6KgUv8dGErPl2eO\\r\\n0G8ZH8RXDcXkxfkJWaTHvMGj8zDeV0pH0PffkFAkuf8l9Hb1Zx\\/OuILz9QpByUVp\\r\\n\\/C5aiDrcz6q1c2kyOF3W7Lcghq2NaCjvAoIBAQDcoBxNP6+km\\/AgTjIQMtU2GusZ\\r\\nxzIKyItpkjYON8GyYJGMTr8twqhhomsW8nrodZAeqo\\/nUvjKGWebjR2ohEsRfqgN\\r\\n6eMTmbEYZDjnxiQyFlc6BwUvRhlaVlFAh3AquYEGd5aKbt5+k9798j1EPhFODFLM\\r\\nhhs6wd00A0den+X\\/j8u6Hv6yIZC5w7E\\/BL+bGFKUSeJTQsVa8+IO\\/2sVXcNXKJtT\\r\\no2DjN0BYoLePapQ5QBimN8SzenAU32QHH+LSdnGHsT97F232p8eaM5quhTTJ7325\\r\\nOaOmzFG5jrdqyNeIOrFTk5nYyQvEpzAVFp87VdLikFMYMyeWC6dIF+9PDk6O\\r\\n-----END RSA PRIVATE KEY-----"}'# noqa: E501
        replaced = util_api.replace_private_key(payload)
        self.assertEqual(replaced, r'{"value": "-----BEGIN RSA PRIVATE KEY-----\******n-----END RSA PRIVATE KEY-----"}') # noqa: W605

# ################################################################################################################################
# ################################################################################################################################

class TestUpdateBindPort(TestCase):

    def test_update_bind_port_zeromq(self):
        config1 = Bunch()
        config1.address = 'tcp://*:37047'

        util_api.update_bind_port(config1, 0)

        self.assertEqual(config1.address, 'tcp://*:37047')
        self.assertEqual(config1.bind_port, 37047)

        config2 = Bunch()
        config2.address = 'tcp://*:47047'

        util_api.update_bind_port(config2, 3)

        self.assertEqual(config2.address, 'tcp://*:47050')
        self.assertEqual(config2.bind_port, 47050)

# ################################################################################################################################

    def test_update_bind_port_websocket(self):

        config1 = Bunch()
        config1.address = 'ws://0.0.0.0:36190'

        util_api.update_bind_port(config1, 0)

        self.assertEqual(config1.address, 'ws://0.0.0.0:36190')
        self.assertEqual(config1.bind_port, 36190)

        config2 = Bunch()
        config2.address = 'wss://example.com:16251'

        util_api.update_bind_port(config2, 3)

        self.assertEqual(config2.address, 'wss://example.com:16254')
        self.assertEqual(config2.bind_port, 16254)

# ################################################################################################################################
# ################################################################################################################################

class TestAPIKeyUsername(TestCase):
    def test_update_apikey_username(self):
        config = Bunch(header='x-aaa')
        util_api.update_apikey_username_to_channel(config)
        self.assertEqual(config.header, 'HTTP_X_AAA')

# ################################################################################################################################
# ################################################################################################################################

class StaticConfigTestCase(TestCase):

    def test_read_file_no_directories(self):

        with TemporaryDirectory() as base_dir:

            file_dir = os.path.join(base_dir)
            file_name = 'foo.txt'
            file_path = os.path.join(file_dir, file_name)

            contents = 'This is a test.'
            Path(file_path).write_text(contents)

            static_config = StaticConfig(base_dir)
            static_config.read_file(file_path, file_name)

            value = static_config[file_name]
            self.assertEqual(value, contents)

# ################################################################################################################################

    def test_read_file_with_one_directory(self):

        with TemporaryDirectory() as base_dir:

            level1 = 'abc'

            file_dir = os.path.join(base_dir, level1)
            file_name = 'foo.txt'
            file_path = os.path.join(file_dir, file_name)

            contents = 'This is a test.'

            Path(file_dir).mkdir(parents=True)
            Path(file_path).write_text(contents)

            static_config = StaticConfig(base_dir)
            static_config.read_file(file_path, file_name)

            value = static_config[level1][file_name]
            self.assertEqual(value, contents)

# ################################################################################################################################

    def test_read_file_with_nested_directory(self):

        with TemporaryDirectory() as base_dir:

            level1 = 'abc'
            level2 = 'zxc'
            level3 = 'qwe'

            file_dir = os.path.join(base_dir, *[level1, level2, level3])
            file_name = 'foo.txt'
            file_path = os.path.join(file_dir, file_name)

            contents = 'This is a test.'

            Path(file_dir).mkdir(parents=True)
            Path(file_path).write_text(contents)

            static_config = StaticConfig(base_dir)
            static_config.read_file(file_path, file_name)

            value = static_config[level1][level2][level3][file_name]
            self.assertEqual(value, contents)

# ################################################################################################################################
# ################################################################################################################################

class SearchResultsTestCase(TestCase):
    def test_from_list(self):

        data_list = [

            # Page 1
            'item1',
            'item2',
            'item3',

            # Page 2
            'item4',
            'item5',
            'item6',

            # Page 3
            'item7',
            'item8',
            'item9',

            # Page 3
            'item10',
            'item11',
            'item12',
        ]

        # Which page are we on in this result object
        cur_page = 2

        # How many results to return in each page
        page_size = 3

        search_results = SearchResults.from_list(data_list, cur_page, page_size, needs_sort=False)
        search_results = search_results.to_dict()

        self.assertIsInstance(search_results, dict)

        self.assertEqual(search_results['num_pages'], 4)
        self.assertEqual(search_results['cur_page'], 2)
        self.assertEqual(search_results['prev_page'], 1)
        self.assertEqual(search_results['next_page'], 3)
        self.assertEqual(search_results['page_size'], 3)
        self.assertEqual(search_results['total'], 12)

        self.assertTrue(search_results['has_prev_page'])
        self.assertTrue(search_results['has_next_page'])

        self.assertListEqual(
            search_results['result'],
            ['item9', 'item8', 'item7']
        )


# ################################################################################################################################
# ################################################################################################################################
