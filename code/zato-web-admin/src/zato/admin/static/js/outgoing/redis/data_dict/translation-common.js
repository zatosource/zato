// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.TranslationEntry = new Class({
    toString: function() {
        var s = '<TranslationEntry id:{0} system1:{1} key1:{2} value1:{3} system2:{4} key2:{5} value2:{6}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.system1 ? this.system1 : '(none)',
                                this.key1 ? this.key1 : '(none)',
                                this.value1 ? this.value1 : '(none)',
                                this.system2 ? this.system2 : '(none)',
                                this.key2 ? this.key2 : '(none)',
                                this.value2 ? this.value2 : '(none)');
    },

    get_name: function() {
        
        var s = 'id:[{0}] system1:[{1}] key1:[{2}] value1:[{3}] system2:[{4}] key2:[{5}] value2:[{6}]';
        return String.format(s, this.id ? this.id : '(none)',
                                this.system1 ? this.system1 : '(none)',
                                this.key1 ? this.key1 : '(none)',
                                this.value1 ? this.value1 : '(none)',
                                this.system2 ? this.system2 : '(none)',
                                this.key2 ? this.key2 : '(none)',
                                this.value2 ? this.value2 : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.kvdb.data_dict.translation.setup_selects = function(change_data) {
    _.each(change_data, function(elem) {
        var source_id = elem[0];
        var target_id = elem[1];
        var url = elem[2];
        var query_items = {}
        var system_no = null;
        
        $('#id_'+ source_id).change(function() {
            _.each(elem[3], function(item, _ignored) {
                _.each(item, function(value, key) {
                    query_items[key] = $('#id_'+ value).val();
                })
            });
            if(source_id.indexOf('system') != -1) {
                system_no = source_id.charAt(source_id.length-1);
                $('#id_value' + system_no).find('option:not([value=""])').remove();
                $('#id_edit-value' + system_no).find('option:not([value=""])').remove();
            }
            $.fn.zato.kvdb.data_dict.translation.update_selects(target_id, url, query_items);
        });
    });
}

$.fn.zato.kvdb.data_dict.translation.update_selects = function(target_id, url, query_items, callback) {

    var query_string = {'cluster':$('#cluster_id').val()};
    _.each(query_items, function(value, key) {
        query_string[key] = value;
    });

    var target = $('#id_'+ target_id);
    var value = '';
    target.find('option:not([value=""])').remove();
    $.getJSON('./'+ url + '/', query_string, function(result) {
        $.each(result, function(idx) {
            value = '<option value="{0}">{1}</option>';
            target.append(String.format(value, result[idx]['name'], result[idx]['name']));
        });
        if(callback) {
            callback()
        }
    });
}
