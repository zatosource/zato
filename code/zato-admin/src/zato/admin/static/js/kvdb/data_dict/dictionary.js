
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.DictEntry = new Class({
    toString: function() {
        var s = '<DictEntry id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.system ? this.system : '(none)',
                                this.key ? this.key : '(none)',
                                this.value ? this.value : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.DictEntry;
    $.fn.zato.data_table.new_row_func = $.fn.zato.kvdb.data_dict.dictionary.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['system', 'key', 'value']);
})

$.fn.zato.kvdb.data_dict.dictionary.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new dictionary entry', null);
}

$.fn.zato.kvdb.data_dict.dictionary.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the dictionary entry', id);
}

$.fn.zato.kvdb.data_dict.dictionary.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var dircache = item.dircache == true;
    
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.host);
    row += String.format('<td>{0}</td>', item.user ? item.user : '');
    row += String.format('<td>{0}</td>', item.acct ? item.acct : '');
    row += String.format('<td>{0}</td>', item.timeout ? item.timeout : '');
    row += String.format('<td>{0}</td>', item.port);
    row += String.format('<td>{0}</td>', dircache ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.data_table.change_password({0})'>Change password</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.kvdb.data_dict.dictionary.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.kvdb.data_dict.dictionary.delete_({0});'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.kvdb.data_dict.dictionary.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing FTP connection [{0}] deleted',
        'Are you sure you want to delete the outgoing FTP connection [{0}]?',
        true);
}
