
if (typeof $.fn.zato === 'undefined') { $.fn.zato = {}; }
if (typeof $.fn.zato.eda === 'undefined') { $.fn.zato.eda = {}; }
$.fn.zato.eda.message_detail = {};

$.fn.zato.eda.message_detail._detect_mode = function(text) {
    var trimmed = text.trim();
    if ((trimmed.charAt(0) === '{' && trimmed.charAt(trimmed.length - 1) === '}') ||
        (trimmed.charAt(0) === '[' && trimmed.charAt(trimmed.length - 1) === ']')) {
        try { JSON.parse(trimmed); return 'json'; } catch(e) {}
    }
    if (trimmed.charAt(0) === '<') return 'xml';
    if (trimmed.indexOf('---') === 0 || /^\w+:\s/m.test(trimmed)) return 'yaml';
    return 'text';
};

$.fn.zato.eda.message_detail.init = function(data) {
    if (!data || !data.msg_id) return;

    var pub_time_local = $.fn.zato.eda.format_local_time(data.pub_time_ts);
    var pub_time_relative = $.fn.zato.eda.relative_time(data.pub_time_ts);

    var $meta = $('#msg-metadata');
    $meta.empty();

    var _card = function(label, value) {
        return '<div class="meta-card"><div class="meta-label">' + label + '</div><div class="meta-value">' + value + '</div></div>';
    };

    $meta.append(_card('Message ID', '<span class="eda-copy-target" id="msg-id-copy" data-copy-value="' + data.msg_id + '">' + data.msg_id + '</span>'));
    $meta.append(_card('Topic', '<a href="/zato/eda/topic/' + encodeURIComponent(data.topic_name || '') + '/?cluster=1">' + (data.topic_name || '-') + '</a>'));
    $meta.append(_card('Published', pub_time_local + ' (' + pub_time_relative + ')'));
    $meta.append(_card('Size', (data.size || 0) + ' bytes'));

    if (data.priority !== undefined && data.priority !== null) {
        $meta.append(_card('Priority', data.priority));
    }

    if (data.expiration !== undefined && data.expiration !== null && data.expiration > 0) {
        var exp_seconds = data.expiration;
        var exp_from_now = '';
        if (data.pub_time_ts) {
            var expire_at_ts = data.pub_time_ts + exp_seconds;
            var expire_at_local = $.fn.zato.eda.format_local_time(expire_at_ts);
            var now_ts = Date.now() / 1000;
            var remaining = expire_at_ts - now_ts;
            exp_from_now = expire_at_local + ' (' + $.fn.zato.eda.humanize_duration(remaining) + ')';
        } else {
            exp_from_now = exp_seconds + ' seconds';
        }
        $meta.append(_card('Expiration', exp_from_now));
    }

    $.fn.zato.eda.bind_copy_targets();

    var raw_data = data.data || '';

    try {
        var parsed = JSON.parse(raw_data);
        if (typeof parsed === 'object' && parsed !== null && parsed.data !== undefined) {
            raw_data = String(parsed.data);
        }
    } catch(e) {}

    var mode = $.fn.zato.eda.message_detail._detect_mode(raw_data);

    var ace_mode = 'ace/mode/text';
    if (mode === 'json') {
        ace_mode = 'ace/mode/json';
        try { raw_data = JSON.stringify(JSON.parse(raw_data), null, 4); } catch(e) {}
    } else if (mode === 'xml') {
        ace_mode = 'ace/mode/xml';
    } else if (mode === 'yaml') {
        ace_mode = 'ace/mode/yaml';
    }

    var editor = ace.edit('msg-data-content');
    editor.setTheme('ace/theme/chrome');
    editor.session.setMode(ace_mode);
    editor.setReadOnly(true);
    editor.setShowPrintMargin(false);
    editor.setValue(raw_data, -1);
    editor.setOptions({
        maxLines: 30,
        minLines: 3,
        fontSize: 13,
        fontFamily: 'monospace'
    });

    var $tbody = $('#delivery-body');
    var statuses = data.delivery_status || [];
    for (var status_idx = 0; status_idx < statuses.length; status_idx++) {
        var item = statuses[status_idx];
        var status_class = 'status-' + (item.status || '').replace(/ /g, '_');
        var sub_link = '<a href="/zato/eda/queue/' + encodeURIComponent(data.topic_name || '') + '/' + encodeURIComponent(item.sub_key) + '/?cluster=1">' + item.sub_key + '</a>';
        $tbody.append('<tr><td>' + sub_link + '</td><td><span class="eda-status-badge ' + status_class + '">' + item.status + '</span></td></tr>');
    }
    if (statuses.length === 0) {
        $tbody.append('<tr><td colspan="2">No subscribers</td></tr>');
    }
};
