
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubQueueMessage = new Class({
    toString: function() {
        var s = '<PubSubQueueMessage id:{0}>';
        return String.format(s, this.id ? this.id : '(none)');
    },
    get_name: function() {
        return this.msg_id;
    }
});
z

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubQueueMessage;
    $.fn.zato.data_table.parse();
})
