/*
 * action-runner.js
 *
 * Reusable "click a link, POST something, show OK or error inline" component.
 * Shows a tippy tooltip on the clicked link with a green check or red x,
 * plus a "Show details" link on error that opens the existing .invoker-modal-* overlay.
 *
 * Public API:
 *
 *   $.fn.zato.action_runner.run({
 *       link_elem: <anchor element>,
 *       url: '<POST target>',
 *       data: '<optional POST body>',
 *       parse: function(jqXHR, textStatus) { return {is_success, label, details_title, details_body}; },
 *       details_modal_title: 'Response'
 *   });
 *
 *   $.fn.zato.action_runner.close_all();
 */

(function() {

$.fn.zato = $.fn.zato || {};

var _spinner_svg = '<svg width="16" height="16" viewBox="0 0 16 16" style="animation:zato-spin .6s linear infinite;vertical-align:middle">' +
    '<circle cx="8" cy="8" r="6" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="2"/>' +
    '<path d="M8 2a6 6 0 0 1 6 6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/></svg>';

var _check_svg = '<svg width="14" height="14" viewBox="0 0 14 14" style="flex-shrink:0;margin-right:5px">' +
    '<circle cx="7" cy="7" r="7" fill="#22863a"/>' +
    '<path d="M4 7.2l2 2 4-4.4" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

var _error_svg = '<svg width="14" height="14" viewBox="0 0 14 14" style="flex-shrink:0;margin-right:5px">' +
    '<circle cx="7" cy="7" r="7" fill="#cb2431"/>' +
    '<path d="M4.5 4.5l5 5M9.5 4.5l-5 5" fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>';

var _hide_timer = null;
var _active_instance = null;
var _details_store = {};
var _details_seq = 0;

function _syntax_highlight_json(json_str) {
    var escaped = json_str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    return escaped.replace(
        /("(\\u[a-fA-F0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
        function(match) {
            var cls = 'hl-number';
            if (/^"/.test(match)) {
                cls = /:$/.test(match) ? 'hl-key' : 'hl-string';
            } else if (/true|false/.test(match)) {
                cls = 'hl-bool';
            } else if (/null/.test(match)) {
                cls = 'hl-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        }
    );
}

function _make_overlay_draggable($overlay) {
    var is_dragging = false;
    var offset_x = 0;
    var offset_y = 0;
    var $content = $overlay.find('.invoker-modal-content');
    var $header = $overlay.find('.invoker-modal-header');

    $header.on('mousedown', function(e) {
        if ($(e.target).is('button, input, a')) return;
        is_dragging = true;
        var rect = $content[0].getBoundingClientRect();
        offset_x = e.clientX - rect.left;
        offset_y = e.clientY - rect.top;
        $content.css({position: 'fixed', margin: '0', left: rect.left + 'px', top: rect.top + 'px', transform: 'none'});
        e.preventDefault();
    });

    $(document).on('mousemove.action_runner_drag', function(e) {
        if (!is_dragging) return;
        $content.css({left: (e.clientX - offset_x) + 'px', top: (e.clientY - offset_y) + 'px'});
    });

    $(document).on('mouseup.action_runner_drag', function() {
        is_dragging = false;
    });
}

function _escape_html(text) {
    return String(text == null ? '' : text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

function _pretty_print_markup(raw) {
    var tokens = raw.match(/(<[^>]+>|[^<]+)/g) || [raw];
    var indent = 0;
    var pad = '  ';
    var lines = [];
    for (var i = 0; i < tokens.length; i++) {
        var t = tokens[i].replace(/^\s+|\s+$/g, '');
        if (!t) continue;
        if (t.charAt(0) === '<') {
            var is_closing = /^<\//.test(t);
            var is_self_closing = /\/>$/.test(t) || /^<!/.test(t) || /^<\?/.test(t)
                || /^<(meta|link|br|hr|img|input|col|area|base|embed|source|track|wbr)\b/i.test(t);
            if (is_closing) {
                indent = Math.max(0, indent - 1);
                lines.push(Array(indent + 1).join(pad) + t);
            } else if (is_self_closing) {
                lines.push(Array(indent + 1).join(pad) + t);
            } else {
                lines.push(Array(indent + 1).join(pad) + t);
                indent++;
            }
        } else {
            lines.push(Array(indent + 1).join(pad) + t);
        }
    }
    return lines.join('\n');
}

function _highlight_markup_tags(escaped) {
    return escaped.replace(/(&lt;\/?[a-zA-Z:][a-zA-Z0-9:._-]*(?:\s[^&]*?)?\/?\s*&gt;)/g,
        '<span class="hl-tag">$1</span>')
        .replace(/(&lt;![a-zA-Z][^&]*?&gt;)/g, '<span class="hl-tag">$1</span>')
        .replace(/(&lt;\?[^?]*\?&gt;)/g, '<span class="hl-tag">$1</span>');
}

function _pretty_print_body(body_text, content_type) {
    content_type = (content_type || '').toLowerCase();

    if (content_type.indexOf('json') !== -1 || content_type.indexOf('javascript') !== -1) {
        try {
            var parsed = JSON.parse(body_text);
            return _syntax_highlight_json(JSON.stringify(parsed, null, 2));
        } catch(e) {}
    }

    if (content_type.indexOf('html') !== -1 || content_type.indexOf('xml') !== -1) {
        var formatted = _pretty_print_markup(body_text);
        return _highlight_markup_tags(_escape_html(formatted));
    }

    try {
        var parsed = JSON.parse(body_text);
        return _syntax_highlight_json(JSON.stringify(parsed, null, 2));
    } catch(e) {}

    var trimmed = body_text.replace(/^\s+/, '');
    if (trimmed.charAt(0) === '<') {
        var formatted = _pretty_print_markup(body_text);
        return _highlight_markup_tags(_escape_html(formatted));
    }

    return _escape_html(body_text);
}

function _default_parse(jqXHR, textStatus) {
    var body = jqXHR.responseText || '';
    var is_http_ok = (jqXHR.status >= 200 && jqXHR.status < 300);

    var parsed = null;
    try {
        parsed = JSON.parse(body);
    } catch(e) {
        parsed = null;
    }

    if(parsed && typeof parsed === 'object') {
        var is_success = !!parsed.is_success;
        var label = parsed.inner_exception_message
            || parsed.exception_message
            || parsed.status_text
            || (is_success ? 'OK' : 'No response');
        var details_body = parsed.info || parsed.exception_message || '';
        var details_title = parsed.exception_message || parsed.status_text || '';
        return {
            is_success: is_success,
            label: label,
            details_title: details_title,
            details_body: details_body
        };
    }

    if(is_http_ok) {
        return {
            is_success: true,
            label: body ? body : 'OK',
            details_title: '',
            details_body: body
        };
    }

    return {
        is_success: false,
        label: body || 'Error',
        details_title: body || 'Error',
        details_body: body
    };
}

function _render_success(instance, label) {
    var html = '<span style="display:inline-flex;align-items:center;white-space:nowrap;font-size:13px;color:#fff">' +
        _escape_html(label) + '</span>';
    instance.setContent(html);
    _hide_timer = setTimeout(function() { instance.hide(); }, 800);
}

function _render_error(instance, label, details_id) {
    var html = '<span style="display:inline-flex;align-items:center;white-space:nowrap;font-size:13px;color:#f97583">' +
        _escape_html(label) + '</span>' +
        '<br><a href="javascript:void(0)" style="font-size:12px;margin-top:2px;display:inline-block" ' +
        'onclick="$.fn.zato.action_runner.show_details(\'' + details_id + '\')">Show details</a>';
    instance.setContent(html);
}

$.fn.zato.action_runner = {

    run: function(opts) {

        var link_elem = opts.link_elem;
        var url = opts.url;
        var data = opts.data || '';
        var parse = opts.parse || _default_parse;
        var on_success = opts.on_success || null;
        var details_modal_title = opts.details_modal_title || 'Response';

        console.log('[action_runner] run: url=' + url + ' data_length=' + data.length + ' has_on_success=' + !!on_success);
        console.log('[action_runner] run: link_elem=' + (link_elem ? link_elem.tagName + '.' + link_elem.className : 'null'));
        console.log('[action_runner] run: tippy available=' + (typeof tippy !== 'undefined'));

        var use_tippy = link_elem && (typeof tippy !== 'undefined');

        if(!use_tippy) {
            console.log('[action_runner] run: no tippy, using fallback');
            var fallback_callback = function(jqXHR, textStatus) {
                console.log('[action_runner] fallback callback: status=' + jqXHR.status + ' textStatus=' + textStatus);
                var r = parse(jqXHR, textStatus);
                $.fn.zato.user_message(r.is_success, r.label);
            };
            $.fn.zato.post(url, fallback_callback, data, 'text', true);
            return;
        }

        if(_hide_timer) {
            clearTimeout(_hide_timer);
            _hide_timer = null;
        }

        if(link_elem._tippy) {
            link_elem._tippy.hide();
            link_elem._tippy.destroy();
        }

        $.fn.zato.action_runner.close_details();

        var instance = tippy(link_elem, {
            content: _spinner_svg,
            allowHTML: true,
            placement: 'top',
            trigger: 'manual',
            arrow: true,
            animation: 'fade',
            duration: [50, 50],
            hideOnClick: false,
            interactive: true,
            appendTo: document.body,
            zIndex: 100001,
        });

        _active_instance = instance;
        instance.show();

        var callback = function(jqXHR, textStatus) {
            console.log('[action_runner] callback: status=' + jqXHR.status + ' textStatus=' + textStatus);
            console.log('[action_runner] callback: responseText=' + (jqXHR.responseText || '').substring(0, 300));
            var r = parse(jqXHR, textStatus);
            console.log('[action_runner] callback: parsed is_success=' + r.is_success + ' label=' + (r.label || '').substring(0, 100));
            if(r.is_success) {
                if(on_success) {
                    on_success(instance, r);
                } else {
                    _render_success(instance, r.label);
                }
            } else {
                _details_seq += 1;
                var details_id = 'action-details-' + _details_seq + '-' + Date.now();
                _details_store[details_id] = {
                    title: details_modal_title,
                    heading: r.details_title || r.label,
                    body: r.details_body || '',
                    body_html: r.details_body_html || '',
                    response_content_type: r.response_content_type || '',
                    status_code: r.status_code || 0,
                    instance: instance
                };
                _render_error(instance, r.label, details_id);
            }
        };

        $.fn.zato.post(url, callback, data, 'text', true);
    },

    show_details: function(details_id) {

        var details = _details_store[details_id];
        if(!details) {
            return;
        }

        if(details.instance) {
            details.instance.hide();
        }

        $.fn.zato.action_runner.close_details();

        var body_text = details.body || '(empty response)';
        var body_html = details.body_html || '';
        var response_content_type = details.response_content_type || '';

        var highlighted_body;
        if(body_html) {
            highlighted_body = body_html;
        } else {
            highlighted_body = _pretty_print_body(body_text, response_content_type);
        }

        var lines = (highlighted_body.match(/\n/g) || []).length + 1;
        var gutter = '';
        for(var i = 1; i <= lines; i++) {
            gutter += '  ' + i + '\n';
        }
        var title_text = details.title || 'Response';
        if (details.status_code) {
            title_text += ': ' + details.status_code;
        }
        var escaped_title = _escape_html(title_text);

        var $overlay = $('<div class="invoker-modal-overlay" data-action-runner-overlay="1" style="z-index:100001">' +
            '<div class="invoker-modal-backdrop"></div>' +
            '<div class="invoker-modal-content" style="width:750px;max-height:80vh;display:flex;flex-direction:column;resize:both;overflow:hidden">' +
                '<div class="invoker-modal-header" style="flex-shrink:0">' +
                    '<h2>' + escaped_title + '</h2>' +
                    '<button class="invoker-modal-close-btn">\u00d7</button>' +
                '</div>' +
                '<div class="invoker-modal-body" style="flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden">' +
                    '<div class="invoker-modal-response-header" style="flex-shrink:0">' +
                        '<span class="invoker-modal-response-label">Response body</span>' +
                        '<a class="invoker-modal-response-copy" href="javascript:void(0)">Copy</a>' +
                    '</div>' +
                    '<div class="invoker-modal-response-wrap" style="flex:1;min-height:0;overflow:auto">' +
                        '<div class="invoker-modal-response-gutter">' + gutter + '</div>' +
                        '<pre class="invoker-modal-response-pre">' + highlighted_body + '</pre>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>');

        $overlay.find('.invoker-modal-backdrop').on('click', function() {
            $.fn.zato.action_runner.close_details();
        });

        $overlay.find('.invoker-modal-close-btn').on('click', function() {
            $.fn.zato.action_runner.close_details();
        });

        $overlay.find('.invoker-modal-response-copy').on('click', function() {
            var text = $overlay.find('.invoker-modal-response-pre').text();
            var copy_link = this;
            navigator.clipboard.writeText(text).then(function() {
                if(typeof tippy !== 'undefined') {
                    var t = tippy(copy_link, {
                        content: 'Copied to clipboard',
                        trigger: 'manual',
                        placement: 'top',
                        animation: 'fade',
                        duration: [50, 50],
                        appendTo: document.body,
                        zIndex: 100002,
                    });
                    t.show();
                    setTimeout(function() { t.hide(); setTimeout(function() { t.destroy(); }, 100); }, 1500);
                }
            });
        });

        $('body').append($overlay);

        _make_overlay_draggable($overlay);
    },

    close_details: function() {
        $('[data-action-runner-overlay]').remove();
        $(document).off('mousemove.action_runner_drag mouseup.action_runner_drag');
    },

    close_all: function() {
        if(_hide_timer) {
            clearTimeout(_hide_timer);
            _hide_timer = null;
        }
        if(_active_instance) {
            try { _active_instance.hide(); } catch(e) {}
            try { _active_instance.destroy(); } catch(e) {}
            _active_instance = null;
        }
        $.fn.zato.action_runner.close_details();
    }

};

$(document).on('keydown.action_runner_esc', function(e) {
    if(e.key === 'Escape') {
        $.fn.zato.action_runner.close_all();
    }
});

})();
