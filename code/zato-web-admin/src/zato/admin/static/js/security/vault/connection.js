
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.VaultConnection = new Class({
    toString: function() {
        var s = '<VaultConnection id:{0} name:{1} client_def:{2} role_id:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                this.name ? this.name : '(none)',
                this.client_def ? this.client_def : '(none)',
                this.role_id ? this.role_id : '(none)');
    }

});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.VaultConnection;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.vault.connection.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'client_def', 'role_id']);
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

    item.name = String.format("{0}:::{1}", item.client_def, data.role_name);

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', data.client_name);
    row += String.format('<td>{0}</td>', data.role_name);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.vault.connection.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.client_def);
    row += String.format("<td class='ignore'>{0}</td>", item.role_id);
    row += String.format("<td class='ignore'>{0}:::{1}</td>", item.client_def, data.role_name);

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
