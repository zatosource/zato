# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import UUID

# pytest
import pytest

# Zato
from zato.common.odata.common import ODataException, ODataVersion
from zato.common.odata.query import encode_params, format_function_params, format_key, format_literal, Query

# ################################################################################################################################
# ################################################################################################################################

class TestFormatLiteral:
    """ Python values render as the OData primitive literals of each version.
    """

    def test_string_is_quoted(self):
        assert format_literal('abc') == "'abc'"

    def test_embedded_quote_is_doubled(self):
        assert format_literal("O'Brien") == "'O''Brien'"

    def test_booleans(self):
        assert format_literal(True) == 'true'
        assert format_literal(False) == 'false'

    def test_none_is_null(self):
        assert format_literal(None) == 'null'

    def test_numbers_pass_through(self):
        assert format_literal(17) == '17'
        assert format_literal(2.5) == '2.5'

    def test_guid_is_bare_in_v4(self):
        value = UUID('11111111-2222-3333-4444-555555555555')
        assert format_literal(value, ODataVersion.V4) == '11111111-2222-3333-4444-555555555555'

    def test_guid_is_wrapped_in_v2(self):
        value = UUID('11111111-2222-3333-4444-555555555555')
        assert format_literal(value, ODataVersion.V2) == "guid'11111111-2222-3333-4444-555555555555'"

# ################################################################################################################################
# ################################################################################################################################

class TestFormatKey:
    """ Entity keys render as the parenthesized predicate of a resource path.
    """

    def test_string_key(self):
        assert format_key('ALFKI') == "'ALFKI'"

    def test_int_key(self):
        assert format_key(10248) == '10248'

    def test_guid_key_v4(self):
        value = UUID('11111111-2222-3333-4444-555555555555')
        assert format_key(value) == '11111111-2222-3333-4444-555555555555'

    def test_composite_key(self):
        key = {'SalesOrder': '1', 'SalesOrderItem': 10}
        assert format_key(key) == "SalesOrder='1',SalesOrderItem=10"

    def test_composite_key_v2_guid(self):
        value = UUID('11111111-2222-3333-4444-555555555555')
        key = {'Id': value, 'Line': 2}
        assert format_key(key, ODataVersion.V2) == "Id=guid'11111111-2222-3333-4444-555555555555',Line=2"

# ################################################################################################################################
# ################################################################################################################################

class TestQueryParams:
    """ The Query builder produces the parameters of each version.
    """

    def test_all_common_options(self):
        query = Query(
            filter="City eq 'Berlin'",
            select=['Name', 'City'],
            expand='Orders',
            orderby=['City desc', 'Name'],
            top=10,
            skip=20,
        )
        params = query.to_params(ODataVersion.V4)

        assert params == {
            '$filter': "City eq 'Berlin'",
            '$select': 'Name,City',
            '$expand': 'Orders',
            '$orderby': 'City desc,Name',
            '$top': '10',
            '$skip': '20',
        }

    def test_count_v4(self):
        params = Query(count=True).to_params(ODataVersion.V4)
        assert params == {'$count': 'true'}

        params = Query(count=False).to_params(ODataVersion.V4)
        assert params == {'$count': 'false'}

    def test_count_becomes_inlinecount_in_v2(self):
        params = Query(count=True).to_params(ODataVersion.V2)
        assert params == {'$inlinecount': 'allpages'}

        params = Query(count=False).to_params(ODataVersion.V2)
        assert params == {'$inlinecount': 'none'}

    def test_search_v4_only(self):
        params = Query(search='blue OR green').to_params(ODataVersion.V4)
        assert params == {'$search': 'blue OR green'}

        with pytest.raises(ODataException):
            _ = Query(search='blue').to_params(ODataVersion.V2)

    def test_apply_v4_only(self):
        params = Query(apply='groupby((Country),aggregate(Amount with sum as Total))').to_params(ODataVersion.V4)
        assert params == {'$apply': 'groupby((Country),aggregate(Amount with sum as Total))'}

        with pytest.raises(ODataException):
            _ = Query(apply='identity').to_params(ODataVersion.V2)

    def test_custom_params_ride_along(self):
        query = Query(top=5, custom={'sap-client': '100', 'search': 'abc'})
        params = query.to_params(ODataVersion.V2)

        assert params == {'$top': '5', 'sap-client': '100', 'search': 'abc'}

    def test_empty_query_is_empty(self):
        assert Query().to_params(ODataVersion.V4) == {}
        assert Query().to_params(ODataVersion.V2) == {}

# ################################################################################################################################
# ################################################################################################################################

class TestQueryString:
    """ Encoding of the parameters into a URL query string.
    """

    def test_dollar_names_stay_unescaped(self):
        query = Query(filter="Name eq 'Ab'", top=3)
        text = query.to_query_string(ODataVersion.V4)

        assert '$filter=' in text
        assert '$top=3' in text

    def test_spaces_are_percent_encoded(self):
        query = Query(filter="City eq 'Berlin'")
        text = query.to_query_string(ODataVersion.V4)

        assert text == "$filter=City%20eq%20'Berlin'"

    def test_quotes_parens_and_commas_survive(self):
        text = encode_params({'$filter': "startswith(Name,'A') and Value gt 7"})

        assert text == "$filter=startswith(Name,'A')%20and%20Value%20gt%207"

    def test_unicode_is_percent_encoded(self):
        text = encode_params({'$filter': "Name eq 'Łódź'"})

        assert '%C5%81' in text
        assert 'Łódź' not in text

# ################################################################################################################################
# ################################################################################################################################

class TestFunctionParams:
    """ Function parameters render as the inline name=value pairs of a V4 call.
    """

    def test_mixed_types(self):
        text = format_function_params({'lat': 33, 'lon': -118.41, 'name': 'LAX'})
        assert text == "lat=33,lon=-118.41,name='LAX'"

    def test_guid_v2(self):
        value = UUID('11111111-2222-3333-4444-555555555555')
        text = format_function_params({'id': value}, ODataVersion.V2)
        assert text == "id=guid'11111111-2222-3333-4444-555555555555'"

# ################################################################################################################################
# ################################################################################################################################
