
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.WSXConnection = new Class({
    toString: function() {
        var s = '<WSXConnection id:{0} name:{1}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name: '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.WSXConnection;
    $.fn.zato.data_table.parse();
})

$.fn.zato.channel.wsx.connection_list.disconnect = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'WebSocket client [{0}] disconnected',
        'Are you sure you want to disconnect WebSocket client [{0}]?',
        true);
}
