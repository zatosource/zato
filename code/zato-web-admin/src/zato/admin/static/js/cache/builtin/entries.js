
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.CacheBuiltinItem = new Class({
    toString: function() {
        var s = '<CacheBuiltinItem key:{0} value:{1}>';
        return String.format(s, this.key ? this.key : '(none)',
                                this.value ? this.value : '(none)');
    },
    get_name: function() {
        return this.key;
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.CacheBuiltinItem;
    $.fn.zato.data_table.new_row_func = $.fn.zato.cache.builtin.data_table.new_row;
    $.fn.zato.data_table.parse();
})

$.fn.zato.cache.builtin.entries.delete_ = function(id) {

    var post_data = {};
    post_data['cluster_id'] = $('#cluster_id').val();
    post_data['cache_id'] = $('#cache_id').val();
    post_data['key'] = id;

    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Key {0} deleted',
        'Are you sure you want to delete key <b>{0}</b>?',
        false, false, './delete/', post_data);
}
