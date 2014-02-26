
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Message = new Class({
    toString: function() {
        var s = '<Message id:{0}>';
        return String.format(s, this.id ? this.id : '(none)');
    },

    get_name: function() {
        return this.id;
    }

});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Message;
    $.fn.zato.data_table.parse();
})

$.fn.zato.pubsub.message.delete_ = function(id, name) {
    var post_data = {
        'id': id,
        'name': name,
        'source_type': $('#source_type').val()
    }
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Message `{0}` deleted',
        'Are you sure you want to delete the topic `{0}`?',
        false, null,
        String.format('/zato/pubsub/message/delete/?cluster={0}', $('#cluster_id').val()),
        post_data);
}
