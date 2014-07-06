
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.KeyCert = new Class({
    toString: function() {
        var s = '<KeyCert id:{0} name:{1} fs_name:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.fs_name ? this.fs_name : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.KeyCert;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.tls.key_cert.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'fs_name']);
})


$.fn.zato.security.tls.key_cert.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? "Yes":"No");
    row += String.format('<td>{0}</td>', item.fs_name);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.tls.key_cert.edit({0});'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.tls.key_cert.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.tls.key_cert.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Upload a new key/cert pair', null);
}

$.fn.zato.security.tls.key_cert.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Upload a key/cert pair', id);
}

$.fn.zato.security.tls.key_cert.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Key and cert [{0}] deleted',
        'Are you sure you want to delete the key and cert [{0}]?',
        true);
}
