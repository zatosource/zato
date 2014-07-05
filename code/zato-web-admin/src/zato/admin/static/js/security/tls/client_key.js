
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.ClientKey = new Class({
    toString: function() {
        var s = '<ClientKey id:{0} name:{1} value:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.value ? this.value : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.ClientKey;
    $.fn.zato.data_table.new_row_func = $.fn.zato.security.tls.client_key.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'value']);
})


$.fn.zato.security.tls.client_key.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.tls.client_key.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.security.tls.client_key.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Client key [{0}] deleted',
        'Are you sure you want to delete the client key [{0}]?',
        true);
}
