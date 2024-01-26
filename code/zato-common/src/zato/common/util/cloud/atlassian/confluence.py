# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.server.service import Model
from zato.common.typing_ import list_, list_field
from zato.common.util.file_system import fs_safe_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class Config:
    ParamName:       str = 'Parameters'
    MacroName:       str = 'details'
    DataLayout:      str = 'default'
    SchemaVersion:   str = '1'

    KeyStyle:        str = 'width: 340.0px;'
    ValueStyle:      str = 'width: 340.0px;'
    UserLinkPattern: str = '<ac:link><ri:user ri:account-id="{account_id}" /></ac:link>'
    RowPattern:      str = """
<tr>
    <th>
        <p>{key}</p>
    </th>
    <td>
        <p>{value}</p>
    </td>
</tr>
    """.rstrip()

    MacroTemplate: str = """
<ac:structured-macro
    ac:name="{macro_name}"
    ac:schema-version="{schema_version}"
    data-layout="default"
    ac:local-id="structured-macro-local-id-{local_id}"
    ac:macro-id="macro-id-{local_id}">

    <ac:parameter ac:name="id">{param_name}</ac:parameter>
    <ac:rich-text-body>
        <table data-layout="default" ac:local-id="table-local-id-{local_id}">
            <colgroup>
                <col style="{key_style}" />
                <col style="{value_style}" />
            </colgroup>
            <tbody>{rows}
            </tbody>
        </table>
    </ac:rich-text-body>
</ac:structured-macro>
""".strip()

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Row(Model):
    key: str
    value: str

# ################################################################################################################################
# ################################################################################################################################

class PageProperties:
    """ Allows one to create a table with a Confluence's Page Properties macro and table.
    """
    param_name:   str = Config.ParamName
    key_style:    str = Config.KeyStyle
    value_style:  str = Config.ValueStyle

    macro_name:        str = Config.MacroName
    row_pattern:       str = Config.RowPattern
    macro_template:    str = Config.MacroTemplate
    schema_version:    str = Config.SchemaVersion
    user_link_pattern: str = Config.UserLinkPattern

    rows: list_[Row] = list_field()

# ################################################################################################################################

    def __init__(self, param_name:'str'='', local_id:'str'='') -> 'None':
        self.param_name = param_name or Config.ParamName
        self.local_id = local_id or 'zato-{}'.format(fs_safe_now())
        self.rows = []

# ################################################################################################################################

    def get_user_link(self, account_id:'str') -> 'str':
        value = self.user_link_pattern.format(account_id=account_id)
        return value

# ################################################################################################################################

    def append(self, key:'any_', value:'any_') -> 'Row':
        row = Row(key=key, value=value)
        self.rows.append(row)
        return row

# ################################################################################################################################

    def get_result(self):

        # To turn all rows into HTML data
        html_rows = []

        # .. convert each one ..
        for row in self.rows:
            html_row = self.row_pattern.format(key=row.key, value=row.value)
            html_rows.append(html_row)

        # .. and build a string representing all the rows.
        rows = '\n'.join(html_rows)

        ctx = {
            'rows':           rows,
            'param_name':     self.param_name,
            'local_id':       self.local_id,
            'key_style':      self.key_style,
            'value_style':    self.value_style,
            'macro_name':     self.macro_name,
            'schema_version': self.schema_version,
        }

        result = self.macro_template.format(**ctx)
        return result

# ################################################################################################################################
# ################################################################################################################################
