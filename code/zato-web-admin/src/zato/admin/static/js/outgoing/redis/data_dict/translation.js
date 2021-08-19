
$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.TranslationEntry;
    $.fn.zato.data_table.new_row_func = $.fn.zato.kvdb.data_dict.translation.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['system1', 'key1', 'value1', 'system2', 'key2', 'value2']);
    
    var change_data = [
        ['system1', 'key1', 'get-key-list', [{'system':'system1'}]],
        ['system2', 'key2', 'get-key-list', [{'system':'system2'}]],
        
        ['key1', 'value1', 'get-value-list', [{'system':'system1', 'key':'key1'}]],
        ['key2', 'value2', 'get-value-list', [{'system':'system2', 'key':'key2'}]],

        ['edit-system1', 'edit-key1', 'get-key-list', [{'system':'edit-system1'}]],
        ['edit-system2', 'edit-key2', 'get-key-list', [{'system':'edit-system2'}]],        
        
        ['edit-key1', 'edit-value1', 'get-value-list', [{'system':'edit-system1', 'key':'edit-key1'}]],
        ['edit-key2', 'edit-value2', 'get-value-list', [{'system':'edit-system2', 'key':'edit-key2'}]],
    ];
    
    $.fn.zato.kvdb.data_dict.translation.setup_selects(change_data);
    
})

$.fn.zato.kvdb.data_dict.translation.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new translation', null);
}

$.fn.zato.kvdb.data_dict.translation.edit = function(id) {

    var instance = $.fn.zato.data_table.data[id];
    
    var _create_edit = function() {
        $.fn.zato.data_table._create_edit('edit', 'Update the translation', id);
    };
    
    var update_value2 = function() {
        $.fn.zato.kvdb.data_dict.translation.update_selects('edit-value2', 'get-value-list', {'system':instance.system2, 'key':instance.key2}, _create_edit)
    };
    
    var update_value1 = function() {
        $.fn.zato.kvdb.data_dict.translation.update_selects('edit-value1', 'get-value-list', {'system':instance.system1, 'key':instance.key1}, update_value2)
    };
    
    var update_key2 = function() {
        $.fn.zato.kvdb.data_dict.translation.update_selects('edit-key2', 'get-key-list', {'system':instance.system2}, update_value1)
    };
    
    var update_key1 = function() {
        $.fn.zato.kvdb.data_dict.translation.update_selects('edit-key1', 'get-key-list', {'system':instance.system1}, update_key2)
    };
    
    update_key1();
    
}

$.fn.zato.kvdb.data_dict.translation.data_table.new_row = function(item, data, include_tr) {
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

$.fn.zato.kvdb.data_dict.translation.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Translation [{0}] deleted',
        'Are you sure you want to delete the translation [{0}]?',
        true);
}
