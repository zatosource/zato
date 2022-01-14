
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.DictEntry = new Class({
    toString: function() {
        var s = '<DictEntry id:{0} system:{1} key:{2} value:{3}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.system ? this.system : '(none)',
                                this.key ? this.key : '(none)',
                                this.value ? this.value : '(none)');
    },

    get_name: function() {
        var s = 'id:[{0}] system:[{1}], key:[{2}], value:[{3}]';
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

    row += "<td class='numbering'>&nbsp;</td>";
    row += String.format('<td>{0}</td>', item.system);
    row += String.format('<td>{0}</td>', item.key);
    row += String.format('<td><pre>{0}</pre></td>', item.value);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.kvdb.data_dict.dictionary.edit({0})'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.kvdb.data_dict.dictionary.delete_({0})'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.kvdb.data_dict.dictionary.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Dictionary entry [{0}] deleted',
        'Are you sure you want to delete the dictionary entry [{0}]?',
        true);
}
