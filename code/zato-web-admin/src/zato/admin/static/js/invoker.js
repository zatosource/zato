/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_invoke_submitted = function() {
    console.debug("on_invoke_submitted: START");
    let current_object_select = $.fn.zato.ide.get_current_object_select();
    let is_modified = current_object_select.attr('data-is-modified') == '1';
    console.debug("on_invoke_submitted: is_modified:", is_modified);

    let request_text = $("#data-request").val();
    console.debug("on_invoke_submitted: request_text from textarea:", JSON.stringify(request_text));
    console.debug("on_invoke_submitted: calling save_request_to_history");
    $.fn.zato.ide.save_request_to_history(request_text);
    console.debug("on_invoke_submitted: after save_request_to_history");

    let invoke_func = function() {
        console.debug("on_invoke_submitted: invoke_func called");
        const options = {
            "request_form_id": "#invoke-service-request-form",
            "on_started_activate_blinking": ["#invoking-please-wait"],
            "on_ended_draw_attention": ["#result-header"],
            "get_request_url_func": $.fn.zato.invoker.get_sync_invoke_request_url,
            "is_invoke": true,
        };
        $.fn.zato.invoker.run_sync_invoker(options);
    };

    if (is_modified) {
        console.debug("on_invoke_submitted: deploying first");
        $.fn.zato.ide.run_sync_deployer(invoke_func);
    } else {
        console.debug("on_invoke_submitted: invoking directly");
        invoke_func();
    }
    console.debug("on_invoke_submitted: END");
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.invoke = function(
    url,
    data,
    callback,
    data_type,
    context
) {
    console.debug("invoke: called with url:", url);
    console.debug("invoke: data:", data);
    data_type = data_type || "JSON";
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        complete: callback,
        dataType: data_type,
        context: context
    });
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.submit_form = function(
    url,
    form_id,
    options,
    on_success_func,
    on_error_func,
    display_timeout,
    data_format,
) {
    console.debug("submit_form: CALLED with url:", url);
    console.debug("submit_form: form_id:", form_id);
    console.debug("submit_form: data_format:", data_format);

    let _display_timeout = display_timeout || 120;
    let form = $(form_id);
    let form_data = form.serialize();
    let _data_format = data_format || null;

    console.debug("submit_form: form_data:", form_data);
    console.debug("submit_form: _display_timeout:", _display_timeout);

    $.ajax({
        type: "POST",
        url: url,
        data: form_data,
        dataType: data_format,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        async: true,

        success: function(data, text_status, request) {
            console.debug("submit_form: success callback triggered");
            console.debug("submit_form: data:", data);
            console.debug("submit_form: text_status:", text_status);
            console.debug("submit_form: request.status:", request.status);
            let _on_success = function() {
                on_success_func(options, data);
            }
            setTimeout(_on_success, _display_timeout)
        },

        error: function(jq_xhr, text_status, error_message) {
            console.debug("submit_form: error callback triggered");
            console.debug("submit_form: jq_xhr.status:", jq_xhr.status);
            console.debug("submit_form: jq_xhr.responseText:", jq_xhr.responseText);
            console.debug("submit_form: text_status:", text_status);
            console.debug("submit_form: error_message:", error_message);
            let _on_error = function() {
                on_error_func(options, jq_xhr, text_status, error_message);
            }
            setTimeout(_on_error, _display_timeout)
        },

    });
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.get_sync_invoke_request_url = function() {
    let select = $("#object-select :selected");
    let service = select.attr("data-service-name");
    console.debug("get_sync_invoke_request_url: select:", JSON.stringify(select));
    console.debug("get_sync_invoke_request_url: service:", JSON.stringify(service));
    let out = "/zato/service/invoke/"+ service + "/cluster/1/";
    console.debug("get_sync_invoke_request_url: out:", JSON.stringify(out));
    return out
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.draw_attention = function(elem_list) {
    // End by draw attention to specific elements
    elem_list.each(function(elem) {
        let _elem = $(elem);
        _elem.removeClass("hidden");
        _elem.removeClass("invoker-draw-attention");
        _elem.addClass("invoker-draw-attention", 1);
    });

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.format_error_traceback = function(response_data) {
    console.debug("format_error_traceback: input response_data type:", typeof response_data);
    console.debug("format_error_traceback: input response_data:", response_data);

    const response_str = JSON.stringify(response_data);
    console.debug("format_error_traceback: stringified response_str:", response_str);
    console.debug("format_error_traceback: response_str length:", response_str.length);

    const has_error_marker = response_str.indexOf("··· Error ···") !== -1;
    console.debug("format_error_traceback: has_error_marker:", has_error_marker);

    if (!has_error_marker) {
        console.debug("format_error_traceback: no error marker found, returning original data");
        return response_data;
    }

    console.debug("format_error_traceback: error marker found, formatting traceback");
    let formatted = response_str;
    console.debug("format_error_traceback: before replacements:", formatted.substring(0, 200));
    formatted = formatted.replace(/^\["/, "");
    formatted = formatted.replace(/"\]$/, "");
    formatted = formatted.replace(/\\n/g, "\n");
    formatted = formatted.replace(/\\"/g, "\"");
    formatted = formatted.replace(/\\\\/g, "\\");
    console.debug("format_error_traceback: after replacements:", formatted.substring(0, 200));
    console.debug("format_error_traceback: final formatted length:", formatted.length);

    return formatted;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_form_ended_common_impl = function(
    options,
    status,
    response,
) {

    let has_response = !!response.data;
    let on_started_activate_blinking = options["on_started_activate_blinking"];
    let on_ended_draw_attention = options["on_ended_draw_attention"];

    // Disable blinking for all the elements that should blink
    on_started_activate_blinking.each(function(elem) {
        $.fn.zato.toggle_css_class($(elem), "invoker-blinking", "hidden");
    });

    // End by draw attention to specific elements
    $.fn.zato.invoker.draw_attention(on_ended_draw_attention);

    // This is optional
    if(response.response_time_human && response.response_time_human != "default") {
        status += " | ";
        status += response.response_time_human;
    }

    if(has_response) {
        if($.fn.zato.is_object(response.data)) {
            response_data = response.data;
        }
        else {
            response_data = response.data;
        }

        if (Array.isArray(response_data) && response_data.length === 1 && typeof response_data[0] === 'string') {
            response_data = response_data[0];
        }

    }
    else {
        response_data = $.fn.zato.to_json(response.data[0].zato_env);
    }

    console.debug("on_form_ended_common_impl: SETTING TEXTAREA NOW");
    $("#result-header").text(status);

    console.debug("on_form_ended_common_impl: response_data before formatting:", response_data);
    console.debug("on_form_ended_common_impl: response_data type:", typeof response_data);

    const formatted_response = $.fn.zato.invoker.format_error_traceback(response_data);

    console.debug("on_form_ended_common_impl: formatted_response:", formatted_response);
    console.debug("on_form_ended_common_impl: formatted_response type:", typeof formatted_response);
    console.debug("on_form_ended_common_impl: ABOUT TO SET #data-response");

    if (typeof formatted_response === "string") {
        console.debug("on_form_ended_common_impl: setting text as string");
        $("#data-response").text(formatted_response);
        console.debug("on_form_ended_common_impl: DONE setting text as string");
    } else {
        console.debug("on_form_ended_common_impl: setting text as JSON.stringify");
        $("#data-response").text(JSON.stringify(formatted_response));
        console.debug("on_form_ended_common_impl: DONE setting text as JSON.stringify");
    }

    let request_text = $("#data-request").val();
    let response_text = $("#data-response").val();
    if ($.fn.zato.ide && $.fn.zato.ide.save_request_to_history && options.is_invoke) {
        $.fn.zato.ide.save_request_to_history(request_text, response_text);
    }
    
    if (window.zato && window.zato.updateMessageViewer) {
        window.zato.updateMessageViewer(response_text);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_form_ended_common = function(
    options,
    status,
    data,
) {

    console.debug("on_form_ended_common: data:", data);
    console.debug("on_form_ended_common: data type:", typeof data);
    console.debug("on_form_ended_common: is_object:", $.fn.zato.is_object(data));

    if($.fn.zato.is_object(data)) {
        var response = data;
    }
    else {
        var response = $.parseJSON(data);
    }

    console.debug("on_form_ended_common: response:", response);
    console.debug("on_form_ended_common: response.data:", response.data);

    $.fn.zato.invoker.on_form_ended_common_impl(options, status, response)

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_sync_invoke_ended_error = function(options, jq_xhr, text_status, error_message) {

    console.debug("on_sync_invoke_ended_error: jq_xhr.responseText:", jq_xhr.responseText);
    console.debug("on_sync_invoke_ended_error: jq_xhr.responseText type:", typeof jq_xhr.responseText);

    let status = jq_xhr.status + " " + error_message;
    $.fn.zato.invoker.on_form_ended_common(options, status, jq_xhr.responseText);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_sync_invoke_ended_success = function(options, data) {

    let status = "200 OK";
    let on_post_success_func = options["on_post_success_func"];

    $.fn.zato.invoker.on_form_ended_common(options, status, data);

    if(on_post_success_func) {
        on_post_success_func();
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.run_sync_form_submitter = function(options) {

    console.debug("run_sync_form_submitter: called with options:", options);

    // Local variables
    let request_form_id = options["request_form_id"];
    let get_request_url_func = options["get_request_url_func"];
    let on_started_activate_blinking = options["on_started_activate_blinking"];
    let on_ended_draw_attention = options["on_ended_draw_attention"];

    console.debug("run_sync_form_submitter: request_form_id:", request_form_id);

    // Obtain the URL we are to invoke
    let url = get_request_url_func();

    console.debug("run_sync_form_submitter: url:", url);

    // Enable blinking for all the elements that should blink
    on_started_activate_blinking.each(function(elem) {
        $.fn.zato.toggle_css_class($(elem), "hidden", "invoker-blinking");
    });

    // Disable all the elements that previously might have needed attention
    on_ended_draw_attention.each(function(elem) {
        let _elem = $(elem);
        _elem.addClass("hidden");
    });

    // Submit the form, if we have one on input
    if(request_form_id) {
        console.debug("run_sync_form_submitter: submitting form");
        $.fn.zato.invoker.submit_form(
            url,
            request_form_id,
            options,
            $.fn.zato.invoker.on_sync_invoke_ended_success,
            $.fn.zato.invoker.on_sync_invoke_ended_error
        )
    } else {
        console.debug("run_sync_form_submitter: no request_form_id, skipping form submission");
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.run_sync_invoker = function(options) {
    console.debug("run_sync_invoker: START");
    $.fn.zato.invoker.run_sync_form_submitter(options);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* Shared history functions (used by both IDE and channel/outconn invoker)                                                      */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.get_history = function(key) {
    let history_json = localStorage.getItem(key);
    if (history_json) {
        return JSON.parse(history_json);
    }
    return [];
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.save_to_history = function(key, request_text, response_text) {
    if (!request_text) {
        request_text = '';
    }

    let history = $.fn.zato.invoker.get_history(key);

    history.unshift({
        text: request_text,
        response: response_text || '',
        timestamp: Date.now()
    });

    if (history.length > 200) {
        history = history.slice(0, 200);
    }

    localStorage.setItem(key, JSON.stringify(history));
    return history;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.delete_history_item = function(key, index) {
    let history = $.fn.zato.invoker.get_history(key);
    history.splice(index, 1);
    localStorage.setItem(key, JSON.stringify(history));
    return history;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.filter_history = function(key, search_text) {
    let history = $.fn.zato.invoker.get_history(key);

    if (!search_text || search_text.trim() === "") {
        return {history: history, is_search_result: false};
    }

    let filtered = history.filter(function(item) {
        let text = typeof item === 'string' ? item : item.text;
        return text.toLowerCase().indexOf(search_text.toLowerCase()) !== -1;
    });

    return {history: filtered, is_search_result: true};
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.format_timestamp = function(timestamp) {
    let now = new Date();
    let then = new Date(timestamp);
    let diffMs = now - then;
    let diffSec = Math.floor(diffMs / 1000);
    let diffMin = Math.floor(diffSec / 60);
    let diffHour = Math.floor(diffMin / 60);
    let diffDay = Math.floor(diffHour / 24);

    let timeStr = then.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });

    if (diffSec < 60) {
        if (diffSec === 0) diffSec = 1;
        return diffSec === 1 ? '1 second ago' : diffSec + ' seconds ago';
    } else if (diffMin < 60) {
        return diffMin === 1 ? '1 minute ago' : diffMin + ' minutes ago';
    } else if (diffHour < 24) {
        return diffHour === 1 ? '1 hour ago' : diffHour + ' hours ago';
    } else if (diffDay === 1) {
        return 'yesterday at ' + timeStr;
    } else if (diffDay < 7) {
        return diffDay + ' days ago at ' + timeStr;
    } else if (diffDay < 14) {
        let dayName = then.toLocaleDateString('en-US', { weekday: 'long' });
        return dayName + ', last week at ' + timeStr;
    } else if (diffDay < 21) {
        let dayName = then.toLocaleDateString('en-US', { weekday: 'long' });
        return dayName + ', two weeks ago at ' + timeStr;
    } else if (diffDay < 60) {
        return 'a month ago at ' + timeStr;
    } else if (diffDay < 365) {
        let months = Math.floor(diffDay / 30);
        return months === 1 ? 'a month ago at ' + timeStr : months + ' months ago at ' + timeStr;
    } else {
        let years = Math.floor(diffDay / 365);
        return years === 1 ? 'a year ago at ' + timeStr : years + ' years ago at ' + timeStr;
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.format_json = function(text) {
    if (!text || typeof text !== 'string') {
        return text || '';
    }
    let trimmed = text.trim();
    if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
        try {
            return JSON.stringify(JSON.parse(trimmed), null, 2);
        } catch (e) {
            return text;
        }
    }
    return text;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.populate_history_list = function(list_container, history, is_search_result, callbacks) {
    list_container.empty();

    if (!history || history.length === 0) {
        let message = is_search_result ? 'No results' : 'Nothing in history';
        list_container.append('<div class="invoker-history-empty">' + message + '</div>');
        return;
    }

    for (let i = 0; i < history.length; i++) {
        $.fn.zato.invoker._render_history_item(list_container, history, i, callbacks);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._render_history_item = function(list_container, history, i, callbacks) {
    let item = history[i];
    let request_text = typeof item === 'string' ? item : item.text;
    let timestamp = typeof item === 'string' ? null : item.timestamp;
    let response = typeof item === 'string' ? '' : (item.response || '');
    let has_response = response && response.trim() !== '' && response.trim() !== '(None)';

    let wrapper = $('<div class="invoker-history-item-wrapper"></div>');
    wrapper.attr("data-index", i);

    let number_box = $('<div class="invoker-history-item-number"></div>').text(i + 1);
    let text_box = $('<div class="invoker-history-item-text"></div>');
    text_box.text(request_text && request_text.trim() !== '' ? request_text : '(No request)');

    let show_response_box = $('<div class="invoker-history-item-show-response"></div>');
    show_response_box.text(has_response ? "Show response" : "(No response)");

    let timestamp_box = $('<div class="invoker-history-item-timestamp"></div>');
    if (timestamp) {
        timestamp_box.text($.fn.zato.invoker.format_timestamp(timestamp));
    }

    let delete_box = $('<div class="invoker-history-item-delete"></div>').text("✕");

    let on_select = function() {
        if (callbacks && callbacks.on_select) {
            callbacks.on_select($(this).closest('.invoker-history-item-wrapper').attr("data-index"));
        }
    };
    text_box.on("click", on_select);
    number_box.on("click", on_select);
    timestamp_box.on("click", on_select);

    show_response_box.on("click", function(e) {
        e.stopPropagation();
        $.fn.zato.invoker._toggle_response_detail(wrapper, i, item);
    });

    delete_box.on("click", function(e) {
        e.stopPropagation();
        if (callbacks && callbacks.on_delete) {
            callbacks.on_delete($(this).closest('.invoker-history-item-wrapper').attr("data-index"));
        }
    });

    wrapper.append(number_box, text_box, show_response_box, timestamp_box, delete_box);
    list_container.append(wrapper);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._toggle_response_detail = function(wrapper, index, item) {
    let detail_id = "invoker-history-response-detail-" + index;
    let existing_detail = $("#" + detail_id);

    if (existing_detail.length > 0) {
        existing_detail.toggleClass("visible");
        return;
    }

    let response = typeof item === 'string' ? '' : (item.response || '');
    let detail = $('<div class="invoker-history-response-detail visible" id="' + detail_id + '"></div>');

    let header = $('<div class="invoker-history-response-detail-header"></div>');
    let title = $('<div class="invoker-history-response-detail-title">Response</div>');
    let copy_btn = $('<button class="invoker-history-response-detail-copy">Copy</button>');

    copy_btn.on("click", function(e) {
        e.stopPropagation();
        if (!response || response.trim() === '' || response.trim() === '(None)') {
            return;
        }
        navigator.clipboard.writeText(response).catch(function() {});
    });

    header.append(title, copy_btn);

    let content = $('<div class="invoker-history-response-detail-content"></div>');
    if (!response || response.trim() === '' || response.trim() === '(None)') {
        content.text('(No response)');
    } else {
        $.fn.zato.invoker._render_highlighted_response(content, response);
    }

    detail.append(header, content);
    wrapper.after(detail);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_history_up = function(key, textarea_selector, current_index) {
    let history = $.fn.zato.invoker.get_history(key);
    if (history.length === 0) {
        return current_index;
    }

    if (typeof current_index !== 'number') {
        current_index = -1;
    }

    let textarea_value = $(textarea_selector).val();
    let new_index = current_index + 1;

    if (current_index === -1 && history.length > 0) {
        let first_text = typeof history[0] === 'string' ? history[0] : history[0].text;
        if (textarea_value === first_text) {
            new_index = 1;
        }
    }

    if (new_index >= history.length) {
        return current_index;
    }

    let item = history[new_index];
    $(textarea_selector).val(typeof item === 'string' ? item : item.text);
    return new_index;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_history_down = function(key, textarea_selector, current_index) {
    let history = $.fn.zato.invoker.get_history(key);
    if (history.length === 0) {
        return current_index;
    }

    if (typeof current_index !== 'number') {
        current_index = -1;
    }

    let new_index = current_index - 1;

    if (new_index < -1) {
        return current_index;
    }

    if (new_index === -1) {
        $(textarea_selector).val("");
    } else {
        let item = history[new_index];
        $(textarea_selector).val(typeof item === 'string' ? item : item.text);
    }
    return new_index;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
/* Invoker modal overlay (channel / outconn)                                                                                    */
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._modal_config = null;

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.render_overlay_html = function() {
    if ($("#invoker-modal-overlay").length > 0) {
        return;
    }

    let html = ''
        + '<div id="invoker-modal-overlay" class="invoker-modal-overlay hidden">'
        +   '<div class="invoker-modal-backdrop"></div>'
        +   '<div class="invoker-modal-content">'
        +     '<div class="invoker-modal-header">'
        +       '<h2 id="invoker-modal-title">Invoke</h2>'
        +       '<button class="invoker-modal-close-btn" id="invoker-modal-close">✕</button>'
        +     '</div>'
        +     '<div class="invoker-modal-body">'
        +       '<form id="invoker-modal-form" novalidate>'
        +         '<textarea id="invoker-modal-request" class="invoker-modal-request-textarea" name="data-request"'
        +           ' placeholder="Enter JSON or key=value pairs, e.g.:\nkey1=value1\nkey2=value2\n\nCtrl+↑/↓ for history, Ctrl+K for full history"></textarea>'
        +       '</form>'
        +       '<div class="invoker-modal-buttons">'
        +         '<input type="button" id="invoker-modal-invoke-btn" class="invoker-btn-primary" value="Invoke" />'
        +         '<input type="button" id="invoker-modal-history-btn" value="History" />'
        +         '<div class="invoker-more-options-toggle">'
        +           '<a href="javascript:$.fn.zato.invoker.toggle_more_options()">More options</a>'
        +         '</div>'
        +       '</div>'
        +       '<div class="invoker-more-options-block hidden" id="invoker-more-options">'
        +         '<div class="invoker-more-options-row">'
        +           '<label>HTTP method</label>'
        +           '<select id="invoker-modal-method">'
        +             '<option value="POST" selected>POST</option>'
        +             '<option value="GET">GET</option>'
        +             '<option value="PUT">PUT</option>'
        +             '<option value="DELETE">DELETE</option>'
        +             '<option value="PATCH">PATCH</option>'
        +             '<option value="OPTIONS">OPTIONS</option>'
        +           '</select>'
        +         '</div>'
        +         '<div class="invoker-more-options-row">'
        +           '<label>Query string</label>'
        +           '<input type="text" id="invoker-modal-query-params" placeholder="key1=val1&key2=val2" />'
        +         '</div>'
        +         '<div class="invoker-more-options-row">'
        +           '<label>Path parameters</label>'
        +           '<input type="text" id="invoker-modal-path-params" placeholder="param1=val1&param2=val2" />'
        +         '</div>'
        +       '</div>'
        +       '<div class="invoker-modal-status" id="invoker-modal-status"></div>'
        +       '<div class="invoker-modal-response-header">'
        +         '<span class="invoker-modal-response-label">Response</span>'
        +         '<span>|</span>'
        +         '<a class="invoker-modal-response-copy" id="invoker-modal-copy-btn" href="javascript:void(0)">Copy</a>'
        +       '</div>'
        +       '<div class="invoker-modal-response-wrap">'
        +         '<div id="invoker-modal-response-gutter" class="invoker-modal-response-gutter"></div>'
        +         '<pre id="invoker-modal-response" class="invoker-modal-response-pre" contenteditable="true" spellcheck="false"></pre>'
        +       '</div>'
        +     '</div>'
        +   '</div>'
        + '</div>';

    $("body").append(html);
    $.fn.zato.invoker._bind_modal_events();
    $.fn.zato.invoker._make_draggable(".invoker-modal-header", ".invoker-modal-content");

    let history_html = ''
        + '<div id="invoker-modal-history-overlay" class="invoker-history-overlay hidden">'
        +   '<div class="invoker-history-overlay-backdrop"></div>'
        +   '<div class="invoker-history-overlay-content">'
        +     '<div class="invoker-history-overlay-header">'
        +       '<h2>Invocation history</h2>'
        +       '<button class="invoker-history-close-btn" id="invoker-modal-history-close">✕</button>'
        +     '</div>'
        +     '<div class="invoker-history-overlay-search">'
        +       '<input type="text" id="invoker-modal-history-search" placeholder="Search history..." />'
        +     '</div>'
        +     '<div class="invoker-history-overlay-list" id="invoker-modal-history-list"></div>'
        +   '</div>'
        + '</div>';

    $("body").append(history_html);
    $.fn.zato.invoker._bind_history_events();
    $.fn.zato.invoker._make_draggable(".invoker-history-overlay-header", ".invoker-history-overlay-content");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._bind_modal_events = function() {
    $("#invoker-modal-close").on("click", $.fn.zato.invoker.close_overlay);
    $(".invoker-modal-backdrop").on("click", $.fn.zato.invoker.close_overlay);
    $("#invoker-modal-invoke-btn").on("click", $.fn.zato.invoker._on_modal_invoke);
    $("#invoker-modal-history-btn").on("click", $.fn.zato.invoker._open_modal_history);
    $("#invoker-modal-copy-btn").on("click", $.fn.zato.invoker._on_copy_response);


    $("#invoker-modal-request").on("keydown", function(e) {
        let is_ctrl = e.ctrlKey || e.metaKey;
        if (is_ctrl && e.key === 'Enter') {
            e.preventDefault();
            $.fn.zato.invoker._on_modal_invoke();
        } else if (is_ctrl && e.key === 'ArrowUp') {
            e.preventDefault();
            $.fn.zato.invoker._on_modal_history_up();
        } else if (is_ctrl && e.key === 'ArrowDown') {
            e.preventDefault();
            $.fn.zato.invoker._on_modal_history_down();
        } else if (is_ctrl && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            $.fn.zato.invoker._open_modal_history();
        }
    });

    $(document).on("keydown.invoker_modal", function(e) {
        if (e.key !== 'Escape') {
            return;
        }
        let history_overlay = $("#invoker-modal-history-overlay");
        if (!history_overlay.hasClass("hidden")) {
            e.preventDefault();
            $.fn.zato.invoker._close_modal_history();
            return;
        }
        let modal_overlay = $("#invoker-modal-overlay");
        if (!modal_overlay.hasClass("hidden")) {
            e.preventDefault();
            $.fn.zato.invoker.close_overlay();
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._bind_history_events = function() {
    $("#invoker-modal-history-close").on("click", $.fn.zato.invoker._close_modal_history);
    $("#invoker-modal-history-overlay .invoker-history-overlay-backdrop").on("click", $.fn.zato.invoker._close_modal_history);

    $("#invoker-modal-history-search").on("input", function() {
        let config = $.fn.zato.invoker._modal_config;
        if (!config) return;
        let result = $.fn.zato.invoker.filter_history(config.history_key, $(this).val());
        $.fn.zato.invoker.populate_history_list(
            $("#invoker-modal-history-list"),
            result.history,
            result.is_search_result,
            $.fn.zato.invoker._get_modal_history_callbacks()
        );
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._get_history_key = function() {
    let config = $.fn.zato.invoker._modal_config;
    return config ? config.history_key : null;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._get_modal_history_callbacks = function() {
    return {
        on_select: function(index) {
            let config = $.fn.zato.invoker._modal_config;
            if (!config) return;
            let history = $.fn.zato.invoker.get_history(config.history_key);
            let item = history[index];
            let request_text = typeof item === 'string' ? item : item.text;
            $("#invoker-modal-request").val(request_text);
            window.zato_invoker_history_index = parseInt(index);
            $.fn.zato.invoker._close_modal_history();
            $("#invoker-modal-request").focus();
        },
        on_delete: function(index) {
            let config = $.fn.zato.invoker._modal_config;
            if (!config) return;
            let history = $.fn.zato.invoker.delete_history_item(config.history_key, index);
            $.fn.zato.invoker.populate_history_list(
                $("#invoker-modal-history-list"),
                history,
                false,
                $.fn.zato.invoker._get_modal_history_callbacks()
            );
        }
    };
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.toggle_more_options = function() {
    $("#invoker-more-options").toggleClass("hidden");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.open_overlay = function(config) {
    $.fn.zato.invoker.render_overlay_html();
    $.fn.zato.invoker._modal_config = config;
    window.zato_invoker_history_index = -1;

    $("#invoker-modal-title").text("Invoke: " + config.name);

    let saved = $.fn.zato.invoker._load_overlay_state(config.history_key);
    let content = $(".invoker-modal-content");

    if (saved.width && saved.height) {
        content.css({"width": saved.width, "height": saved.height});
    } else {
        content.css({"width": "", "height": ""});
    }

    if (saved.left && saved.top) {
        content.css({"position": "fixed", "left": saved.left, "top": saved.top, "margin": "0", "transform": "none"});
    } else {
        content.css({"position": "", "left": "", "top": "", "margin": "", "transform": ""});
    }

    $("#invoker-modal-request").val(saved.request || '');
    $("#invoker-modal-method").val(saved.method || 'POST');
    $("#invoker-modal-query-params").val(saved.query_params || '');
    $("#invoker-modal-path-params").val(saved.path_params || '');
    $("#invoker-modal-status").text(saved.status || '');

    if (saved.response_raw) {
        let pre = $("#invoker-modal-response");
        pre.data("raw-response", saved.response_raw);
        $.fn.zato.invoker._render_highlighted_response(pre, saved.response_raw);
    } else {
        $("#invoker-modal-response").text("").removeData("raw-response");
        $("#invoker-modal-response-gutter").text("");
    }

    if (saved.more_options_open) {
        $("#invoker-more-options").removeClass("hidden");
    } else {
        $("#invoker-more-options").addClass("hidden");
    }

    $("#invoker-modal-overlay").removeClass("hidden");
    $("#invoker-modal-request").focus();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.close_overlay = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (config) {
        $.fn.zato.invoker._save_overlay_state(config.history_key);
    }
    $("#invoker-modal-overlay").addClass("hidden");
    $.fn.zato.invoker._modal_config = null;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._save_overlay_state = function(history_key) {
    let content = $(".invoker-modal-content");
    let rect = content[0].getBoundingClientRect();
    let state = {
        width: content[0].style.width || (rect.width + 'px'),
        height: content[0].style.height || (rect.height + 'px'),
        left: content[0].style.left || '',
        top: content[0].style.top || '',
        request: $("#invoker-modal-request").val() || '',
        method: $("#invoker-modal-method").val() || 'POST',
        query_params: $("#invoker-modal-query-params").val() || '',
        path_params: $("#invoker-modal-path-params").val() || '',
        response_raw: $("#invoker-modal-response").data("raw-response") || '',
        status: $("#invoker-modal-status").text() || '',
        more_options_open: !$("#invoker-more-options").hasClass("hidden")
    };
    localStorage.setItem('zato_invoker_state_' + history_key, JSON.stringify(state));
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._load_overlay_state = function(history_key) {
    let raw = localStorage.getItem('zato_invoker_state_' + history_key);
    if (raw) {
        try {
            return JSON.parse(raw);
        } catch (e) {}
    }
    return {};
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.collect_form_data = function() {
    let data = {
        'data-request': $("#invoker-modal-request").val() || '',
        'request_method': $("#invoker-modal-method").val() || 'POST',
        'query_params': $("#invoker-modal-query-params").val() || '',
        'path_params': $("#invoker-modal-path-params").val() || ''
    };
    return data;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._on_modal_invoke = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (!config) return;

    let form_data = $.fn.zato.invoker.collect_form_data();
    let url = config.get_invoke_url_func(config.id);

    $.fn.zato.invoker.save_to_history(config.history_key, form_data['data-request']);
    $.fn.zato.invoker._set_modal_invoking();

    $.ajax({
        type: 'POST',
        url: url,
        data: form_data,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            $.fn.zato.invoker._on_modal_invoke_success(data, form_data['data-request']);
        },
        error: function(jq_xhr, text_status, error_message) {
            $.fn.zato.invoker._on_modal_invoke_error(jq_xhr, form_data['data-request']);
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._set_modal_invoking = function() {
    $("#invoker-modal-status").text("Invoking ...").addClass("invoker-blinking");
    $("#invoker-modal-response").text("").removeData("raw-response");
    $("#invoker-modal-response-gutter").text("");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._on_modal_invoke_success = function(data, request_text) {
    let response = typeof data === 'string' ? JSON.parse(data) : data;
    let status = "200 OK";

    if (response.response_time_human) {
        status += " | " + response.response_time_human;
    }

    let response_text = '';
    if (response.data !== undefined && response.data !== null) {
        response_text = typeof response.data === 'string' ? response.data : JSON.stringify(response.data, null, 2);
    }

    $.fn.zato.invoker._set_modal_result(status, response_text, request_text);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._on_modal_invoke_error = function(jq_xhr, request_text) {
    let status = jq_xhr.status + " " + (jq_xhr.statusText || "Error");
    let response_text = jq_xhr.responseText || '';

    try {
        let parsed = JSON.parse(response_text);
        if (parsed.data !== undefined) {
            response_text = typeof parsed.data === 'string' ? parsed.data : JSON.stringify(parsed.data, null, 2);
        }
        if (parsed.response_time_human) {
            status += " | " + parsed.response_time_human;
        }
    } catch (e) {
        // responseText is not JSON, use as-is
    }

    $.fn.zato.invoker._set_modal_result(status, response_text, request_text);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._set_modal_result = function(status, response_text, request_text) {
    $("#invoker-modal-status").text(status).removeClass("invoker-blinking");

    let formatted = $.fn.zato.invoker._format_response_text(response_text);
    let pre = $("#invoker-modal-response");
    pre.data("raw-response", formatted);
    $.fn.zato.invoker._render_highlighted_response(pre, formatted);

    let config = $.fn.zato.invoker._modal_config;
    if (config) {
        $.fn.zato.invoker.save_to_history(config.history_key, request_text, response_text);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._on_format_response = function() {
    let pre = $("#invoker-modal-response");
    let raw = pre.data("raw-response") || pre.text() || '';
    let formatted = $.fn.zato.invoker._format_response_text(raw);
    pre.data("raw-response", formatted);
    $.fn.zato.invoker._render_highlighted_response(pre, formatted);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._format_response_text = function(text) {
    if (!text || typeof text !== 'string') {
        return text || '';
    }
    let trimmed = text.trim();

    if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
        try {
            return JSON.stringify(JSON.parse(trimmed), null, 2);
        } catch (e) {}
    }

    if (trimmed.startsWith('<') && trimmed.endsWith('>')) {
        return $.fn.zato.invoker._format_xml(trimmed);
    }

    return text;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._format_xml = function(xml_text) {
    let indent = 0;
    let lines = [];
    let tokens = xml_text.replace(/>\s*</g, '>\n<').split('\n');

    for (let i = 0; i < tokens.length; i++) {
        let token = tokens[i].trim();
        if (!token) {
            continue;
        }
        let is_closing = token.startsWith('</');
        let is_self_closing = token.endsWith('/>') || token.startsWith('<?');

        if (is_closing) {
            indent = Math.max(0, indent - 1);
        }

        lines.push('  '.repeat(indent) + token);

        if (!is_closing && !is_self_closing) {
            indent++;
        }
    }

    return lines.join('\n');
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._render_highlighted_response = function(pre_elem, text) {
    if (!text) {
        pre_elem.html('');
        pre_elem.removeClass('syntax-monokai');
        $.fn.zato.invoker._update_line_numbers(pre_elem);
        return;
    }

    pre_elem.text(text);
    pre_elem.removeClass('syntax-monokai');
    $.fn.zato.invoker._update_line_numbers(pre_elem);

    $.ajax({
        type: 'POST',
        url: '/zato/http-soap/highlight/',
        data: {text: text},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            if (data.html) {
                pre_elem.html(data.html);
                pre_elem.addClass('syntax-monokai');
                $.fn.zato.invoker._update_line_numbers(pre_elem);
            }
        }
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._update_line_numbers = function(pre_elem) {
    let gutter = pre_elem.siblings(".invoker-modal-response-gutter");
    if (gutter.length === 0) {
        gutter = pre_elem.parent().find(".invoker-modal-response-gutter");
    }
    if (gutter.length === 0) {
        return;
    }

    let rendered_text = pre_elem.text();
    if (!rendered_text) {
        gutter.html('');
        return;
    }

    let line_count = rendered_text.split('\n').length;
    let lines = [];
    for (let i = 1; i <= line_count; i++) {
        lines.push(i + ' ');
    }
    gutter.text(lines.join('\n'));
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._on_copy_response = function() {
    let pre = $("#invoker-modal-response");
    let raw = pre.data("raw-response") || pre.text() || '';
    if (!raw.trim()) {
        return;
    }

    let link = $("#invoker-modal-copy-btn");
    navigator.clipboard.writeText(raw).then(function() {
        $.fn.zato.invoker._show_copied_tooltip(link);
    }).catch(function() {});
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._show_copied_tooltip = function(anchor_elem) {
    let offset = anchor_elem.offset();
    let tooltip = $('<span class="invoker-copied-tooltip">Copied to clipboard</span>');
    tooltip.css({
        "position": "fixed",
        "top": (offset.top - $(window).scrollTop() + anchor_elem.outerHeight() / 2 - 10) + "px",
        "left": (offset.left + anchor_elem.outerWidth() + 8) + "px"
    });
    $("body").append(tooltip);
    setTimeout(function() {
        tooltip.remove();
    }, 600);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._make_draggable = function(header_selector, content_selector) {
    let is_dragging = false;
    let offset_x = 0;
    let offset_y = 0;

    $(header_selector).on("mousedown", function(e) {
        if ($(e.target).is("button, input, a")) {
            return;
        }
        is_dragging = true;
        let content = $(content_selector);
        let rect = content[0].getBoundingClientRect();
        offset_x = e.clientX - rect.left;
        offset_y = e.clientY - rect.top;

        content.css("position", "fixed");
        content.css("margin", "0");
        content.css("left", rect.left + "px");
        content.css("top", rect.top + "px");
        content.css("transform", "none");
        e.preventDefault();
    });

    $(document).on("mousemove", function(e) {
        if (!is_dragging) {
            return;
        }
        let content = $(content_selector);
        content.css("left", (e.clientX - offset_x) + "px");
        content.css("top", (e.clientY - offset_y) + "px");
    });

    $(document).on("mouseup", function() {
        is_dragging = false;
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._on_modal_history_up = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (!config) return;
    window.zato_invoker_history_index = $.fn.zato.invoker.on_history_up(
        config.history_key, "#invoker-modal-request", window.zato_invoker_history_index);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._on_modal_history_down = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (!config) return;
    window.zato_invoker_history_index = $.fn.zato.invoker.on_history_down(
        config.history_key, "#invoker-modal-request", window.zato_invoker_history_index);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._open_modal_history = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (!config) return;

    let history = $.fn.zato.invoker.get_history(config.history_key);
    $.fn.zato.invoker.populate_history_list(
        $("#invoker-modal-history-list"),
        history,
        false,
        $.fn.zato.invoker._get_modal_history_callbacks()
    );

    $(".invoker-history-overlay-content").css({"position": "", "left": "", "top": "", "margin": "", "transform": ""});
    $("#invoker-modal-history-overlay").removeClass("hidden");
    $("#invoker-modal-history-search").val("").focus();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker._close_modal_history = function() {
    $("#invoker-modal-history-overlay").addClass("hidden");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
