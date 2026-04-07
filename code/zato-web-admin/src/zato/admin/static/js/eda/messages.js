
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

    for (var msg_idx = 0; msg_idx < messages.length; msg_idx++) {
        var msg = messages[msg_idx];
        var rel = $.fn.zato.eda.relative_time(msg.pub_time_ts);
        var topic = msg.topic_name || '';
        var row = '<tr>';
        row += '<td style="font-family:monospace; font-size:12px"><a href="/zato/eda/messages/' + encodeURIComponent(topic) + '/' + encodeURIComponent(msg.msg_id) + '/?cluster=1">' + msg.msg_id + '</a></td>';
        row += '<td><a href="/zato/eda/topic/' + encodeURIComponent(topic) + '/?cluster=1">' + topic + '</a></td>';
        row += '<td class="data-preview">' + $('<span>').text(msg.data_preview || '').html() + '</td>';
        row += '<td>' + (msg.size || 0) + ' B</td>';
        row += '<td title="' + $.fn.zato.eda.format_local_time(msg.pub_time_ts) + '">' + rel + '</td>';
        row += '</tr>';
        $tbody.append(row);
    }
};

$.fn.zato.eda.messages.init = function(messages, total, page, total_pages, topics, topic_name_filter) {
    if (typeof messages === 'string') { try { messages = JSON.parse(messages); } catch(e) { messages = []; } }

    var $select = $('#messages-topic-select');
    if (topics && topics.length > 0) {
        for (var topic_idx = 0; topic_idx < topics.length; topic_idx++) {
            var selected = (topics[topic_idx].name === topic_name_filter) ? ' selected' : '';
            $select.append('<option value="' + topics[topic_idx].name + '"' + selected + '>' + topics[topic_idx].name + '</option>');
        }
    }

    $select.chosen({
        width: '300px',
        search_contains: true,
        allow_single_deselect: true,
        no_results_text: 'No matching topic'
    });

    $select.on('change', function() {
        $('#messages-filter-form').submit();
    });

    $.fn.zato.eda.messages.render(messages);
    $('#msg-total').text($.fn.zato.eda.format_number(total));
    $('#msg-total-label').text($.fn.zato.eda.pluralize(total, 'message'));
};
