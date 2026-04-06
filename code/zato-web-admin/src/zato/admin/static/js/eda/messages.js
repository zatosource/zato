
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.messages = {};

$.fn.zato.eda.messages.render = function(messages) {
    var $tbody = $('#messages-body');
    $tbody.empty();

    if (!messages || messages.length === 0) {
        $tbody.append('<tr><td colspan="5">No messages found</td></tr>');
        return;
    }

    for (var i = 0; i < messages.length; i++) {
        var m = messages[i];
        var rel = $.fn.zato.eda.relative_time(m.pub_time_ts);
        var row = '<tr>';
        row += '<td><a href="/zato/eda/messages/' + encodeURIComponent(m.stream_name) + '/' + encodeURIComponent(m.msg_id) + '/?cluster=1">' + m.msg_id.substring(0, 15) + '...</a></td>';
        row += '<td><a href="/zato/eda/topic/' + encodeURIComponent(m.stream_name) + '/?cluster=1">' + m.stream_name + '</a></td>';
        row += '<td class="data-preview">' + $('<span>').text(m.data_preview || '').html() + '</td>';
        row += '<td>' + (m.size || 0) + ' B</td>';
        row += '<td title="' + (m.pub_time_ts ? new Date(m.pub_time_ts * 1000).toISOString() : '') + '">' + rel + '</td>';
        row += '</tr>';
        $tbody.append(row);
    }
};

$.fn.zato.eda.messages.init = function(messages, total, page, total_pages) {
    $.fn.zato.eda.messages.render(messages);
    $('#msg-total').text($.fn.zato.eda.format_number(total));
};
