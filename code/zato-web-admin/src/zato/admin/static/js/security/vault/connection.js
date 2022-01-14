
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.VaultConnection = new Class({
    toString: function() {
        var s = '<VaultConnection id:{0} name:{1}>';
        return String.format(s, this.id ? this.id : '(none)',
                this.name ? this.name : '(none)');
    }

});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.VaultConnection;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.vault.connection.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'url', 'timeout']);
})


$.fn.zato.security.vault.connection.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new Vault connection', null);
}

$.fn.zato.security.vault.connection.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the Vault connection', id);
}

$.fn.zato.security.vault.connection.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    if(data.service_name) {
        var service_name = String.format(
            '<a href="/zato/service/overview/{0}/?cluster={1}">{0}</a>', data.service_name, item.cluster_id);
    }
    else {
        var service_name = "<span class='form_hint'>(None)</span>";
    };

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', item.url);
    row += String.format('<td>{0}</td>', item.default_auth_method ? item.default_auth_method : "<span class='form_hint'>(None)</span>");
    row += String.format('<td>{0}</td>', service_name);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.vault.connection.edit({0});'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.vault.connection.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.allow_redirects);
    row += String.format("<td class='ignore'>{0}</td>", item.tls_verify);
    row += String.format("<td class='ignore'>{0}</td>", item.token);
    row += String.format("<td class='ignore'>{0}</td>", data.service_id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.vault.connection.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Vault connection [{0}] deleted',
        'Are you sure you want to delete the Vault connection [{0}]?',
        true);
}
