
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.SalesforceOutconn = new Class({
    toString: function() {
        var s = '<SalesforceOutconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.SalesforceOutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cloud.salesforce.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'api_version',
        'address',
        'username',
        'password',
        'consumer_key',
        'consumer_secret',
    ]);
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.salesforce.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Salesforce connection', null);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.salesforce.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Salesforce connection', id);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.salesforce.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    let cluster_id = $(document).getUrlParam('cluster');

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.address);

    // 2
    row += String.format("<td>{0}</td>", item.username);
    row += String.format('<!--<td><a href="/zato/cloud/salesforce/invoke/{0}/{1}/{2}/?cluster={3}">Invoke</a></td>-->',
        item.id, item.name, $.fn.zato.slugify(item.name), cluster_id);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.cloud.salesforce.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cloud.salesforce.delete_({0});'>Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.ping({0});'>Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    // 4
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.username);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.cloud.salesforce.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Salesforce connection `{0}` deleted',
        'Are you sure you want to delete Salesforce connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
