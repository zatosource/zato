
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.TranslationEntry = new Class({
    toString: function() {
        var s = '<TranslationEntry id:{0} system1:{1} key1:{2} value1:{3} system2:{4} key2:{5} value2:{6}>';
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
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.TranslationEntry;
    $.fn.zato.data_table.new_row_func = $.fn.zato.kvdb.data_dict.translation.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['system1', 'key1', 'value1', 'system2', 'key2', 'value2']);
    
    var change_data = [
        ['system1', 'key1', 'get-key-list', [{'system':'system1'}]],
        ['system2', 'key2', 'get-key-list', [{'system':'system2'}]],
        
        ['key1', 'value1', 'get-value-list', [{'system':'system1', 'key':'key1'}]],
        ['key2', 'value2', 'get-value-list', [{'system':'system2', 'key':'key2'}]],
    ];
    
    _.each(change_data, function(elem) {
        var source_id = elem[0];
        var target_id = elem[1];
        var url = elem[2];
        
        $('#id_'+ source_id).change(function() {

            var query_string = {'cluster':$('#cluster_id').val()};
            _.each(elem[3], function(item, _ignored) {
                _.each(item, function(value, key) {
                    query_string[key] = $('#id_'+ value).val();
                })
            });
        
            var target = $('#id_'+ target_id);
            var value = '';
            target.find('option:not([value=""])').remove();
            $.getJSON('./'+ url + '/', query_string, function(result) {
                $.each(result, function(idx) {
                    value = '<option value="{0}">{1}</option>';
                    target.append(String.format(value, result[idx]['name'], result[idx]['name']));
                });
            });
        });
    });

})

$.fn.zato.kvdb.data_dict.translation.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new translation', null);
}

$.fn.zato.kvdb.data_dict.translation.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the translation', id);
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
