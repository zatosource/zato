
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.TranslationEntry = new Class({
    toString: function() {
        var s = '<DictEntry id:{0} system1:{1} key1:{2} value1:{3} system2:{4} key2:{5} value2:{6}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.system1 ? this.system1 : '(none)',
                                this.key1 ? this.key1 : '(none)',
                                this.value1 ? this.value1 : '(none)',
                                this.system2 ? this.system : '(none)',
                                this.key2 ? this.key2 : '(none)',
                                this.value2 ? this.value2 : '(none)');
    },

    get_name: function() {
        var s = 'id:[{0}] system1:[{1}] key1:[{2}] value1:[{3}] system2:[{4}] key2:[{5}] value2:[{6}]';
        return String.format(s, this.id ? this.id : '(none)',
                                this.system1 ? this.system1 : '(none)',
                                this.key1 ? this.key1 : '(none)',
                                this.value1 ? this.value1 : '(none)',
                                this.system2 ? this.system : '(none)',
                                this.key2 ? this.key2 : '(none)',
                                this.value2 ? this.value2 : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.DictEntry;
    $.fn.zato.data_table.new_row_func = $.fn.zato.kvdb.data_dict.dictionary.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['system1', 'key1', 'value1', 'system2', 'key2', 'value2']);
})

$.fn.zato.kvdb.data_dict.dictionary.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new translation', null);
}

$.fn.zato.kvdb.data_dict.dictionary.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the translation', id);
}

$.fn.zato.kvdb.data_dict.dictionary.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    row += "<td class='numbering'>&nbsp;</td>";
    row += String.format('<td>{0}</td>', item.system1);
    row += String.format('<td>{0}</td>', item.key1);
    row += String.format('<td><pre>{0}</pre></td>', item.value1);
    row += String.format('<td>{0}</td>', item.system2);
    row += String.format('<td>{0}</td>', item.key2);
    row += String.format('<td><pre>{0}</pre></td>', item.value2);
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.kvdb.data_dict.translation.edit({0})'>Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.kvdb.data_dict.translation.delete_({0})'>Delete</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

$.fn.zato.kvdb.data_dict.dictionary.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Translation [{0}] deleted',
        'Are you sure you want to delete the translation [{0}]?',
        true);
}
