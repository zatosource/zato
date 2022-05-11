
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.JiraOutconn = new Class({
    toString: function() {
        var s = '<JiraOutconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.JiraOutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cloud.jira.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'api_version',
        'address',
        'username',
    ]);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.jira.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Jira connection', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.jira.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Jira connection', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.jira.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    let is_cloud = item.is_cloud == true;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);

    // 2
    row += String.format("<td>{0}</td>", item.username);
    row += String.format("<td>{0}</td>", item.api_version);
    row += String.format('<td>{0}</td>', is_cloud ? 'Yes' : 'No');

    // 3
    row += String.format('<td>{0}</td>',
        String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}', 'Change API token')\">Change API token</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.jira.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cloud.jira.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.username);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.jira.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Jira connection `{0}` deleted',
        'Are you sure you want to delete Jira connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
