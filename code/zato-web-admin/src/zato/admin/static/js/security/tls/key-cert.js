
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.KeyCert = new Class({
    toString: function() {
        var s = '<KeyCert id:{0} name:{1} info:{2} auth_data:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.info ? this.info : '(none)',
                                this.auth_data ? this.auth_data : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.KeyCert;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.tls.key_cert.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'auth_data']);
})


$.fn.zato.security.tls.key_cert.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', data.info);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.tls.key_cert.edit({0});'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.tls.key_cert.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.auth_data);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.tls.key_cert.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Upload a new client key and certificate pair', null);
}

$.fn.zato.security.tls.key_cert.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Edit a client key and certificate pair', id);
}

$.fn.zato.security.tls.key_cert.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Client key and certificate [{0}] deleted',
        'Are you sure you want to delete the client key and certificate pair [{0}]?',
        true);
}
