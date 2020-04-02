
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.PubSubMessage = new Class({
    toString: function() {
        var s = '<PubSubMessage id:{0}>';
        return String.format(s, this.id ? this.id : '(none)');
    },
    get_name: function() {
        return this.msg_id;
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.PubSubMessage;
    $.fn.zato.data_table.parse();
})
