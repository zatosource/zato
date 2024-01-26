# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.util.cloud.atlassian.confluence import PageProperties

# ################################################################################################################################
# ################################################################################################################################

class PagePropertiesTestCase(TestCase):

    maxDiff = 1234567890

    def test_create_page_properties(self):

        param_name = 'My Parameter'
        local_id = 'abc-my-local-id'

        prop = PageProperties(param_name, local_id=local_id)

        key1 = 'my.key.1'
        key2 = 'my.key.2'
        key3 = 'my.user'

        value1 = 'my.value.1'
        value2 = 'my.value.2'
        value3 = prop.get_user_link(key3)

        prop.append(key1, value1)
        prop.append(key2, value2)
        prop.append(key3, value3)

        result = prop.get_result()

        expected = """
<ac:structured-macro
    ac:name="details"
    ac:schema-version="1"
    data-layout="default"
    ac:local-id="structured-macro-local-id-abc-my-local-id"
    ac:macro-id="macro-id-abc-my-local-id">

    <ac:parameter ac:name="id">My Parameter</ac:parameter>
    <ac:rich-text-body>
        <table data-layout="default" ac:local-id="table-local-id-abc-my-local-id">
            <colgroup>
                <col style="width: 340.0px;" />
                <col style="width: 340.0px;" />
            </colgroup>
            <tbody>
<tr>
    <th>
        <p>my.key.1</p>
    </th>
    <td>
        <p>my.value.1</p>
    </td>
</tr>

<tr>
    <th>
        <p>my.key.2</p>
    </th>
    <td>
        <p>my.value.2</p>
    </td>
</tr>

<tr>
    <th>
        <p>my.user</p>
    </th>
    <td>
        <p><ac:link><ri:user ri:account-id="my.user" /></ac:link></p>
    </td>
</tr>
            </tbody>
        </table>
    </ac:rich-text-body>
</ac:structured-macro>
        """.strip()

        self.assertEqual(expected, result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
