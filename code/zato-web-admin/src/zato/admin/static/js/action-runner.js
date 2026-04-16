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

function _escape_html(text) {
    return String(text == null ? '' : text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
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
    var html = '<span style="display:inline-flex;align-items:center;white-space:nowrap;font-size:13px;color:#85e89d">' +
        _check_svg + _escape_html(label) + '</span>';
    instance.setContent(html);
    _hide_timer = setTimeout(function() { instance.hide(); }, 3000);
}

function _render_error(instance, label, details_id) {
    var html = '<span style="display:inline-flex;align-items:center;white-space:nowrap;font-size:13px;color:#f97583">' +
        _error_svg + _escape_html(label) + '</span>' +
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
        var details_modal_title = opts.details_modal_title || 'Response';

        var use_tippy = link_elem && (typeof tippy !== 'undefined');

        if(!use_tippy) {
            var fallback_callback = function(jqXHR, textStatus) {
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
        });

        _active_instance = instance;
        instance.show();

        var callback = function(jqXHR, textStatus) {
            var r = parse(jqXHR, textStatus);
            if(r.is_success) {
                _render_success(instance, r.label);
            } else {
                _details_seq += 1;
                var details_id = 'action-details-' + _details_seq + '-' + Date.now();
                _details_store[details_id] = {
                    title: details_modal_title,
                    heading: r.details_title || r.label,
                    body: r.details_body || '',
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
        var lines = body_text.split('\n');
        var gutter = '';
        for(var i = 1; i <= lines.length; i++) {
            gutter += '  ' + i + '\n';
        }
        var escaped_body = _escape_html(body_text);
        var escaped_title = _escape_html(details.title || 'Response');

        var $overlay = $('<div class="invoker-modal-overlay" data-action-runner-overlay="1">' +
            '<div class="invoker-modal-backdrop"></div>' +
            '<div class="invoker-modal-content" style="width:750px;height:auto;max-height:80vh;resize:none">' +
                '<div class="invoker-modal-header">' +
                    '<h2>' + escaped_title + '</h2>' +
                    '<button class="invoker-modal-close-btn">\u00d7</button>' +
                '</div>' +
                '<div class="invoker-modal-body">' +
                    '<div class="invoker-modal-response-header">' +
                        '<span class="invoker-modal-response-label">Response body</span>' +
                        '<a class="invoker-modal-response-copy" href="javascript:void(0)">Copy</a>' +
                    '</div>' +
                    '<div class="invoker-modal-response-wrap">' +
                        '<div class="invoker-modal-response-gutter">' + gutter + '</div>' +
                        '<pre class="invoker-modal-response-pre">' + escaped_body + '</pre>' +
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
                    });
                    t.show();
                    setTimeout(function() { t.hide(); setTimeout(function() { t.destroy(); }, 100); }, 1500);
                }
            });
        });

        $('body').append($overlay);
    },

    close_details: function() {
        $('[data-action-runner-overlay]').remove();
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
