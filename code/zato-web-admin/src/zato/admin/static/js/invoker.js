// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.on_invoke_submitted = function() {
    let currentObjectSelect = $.fn.zato.ide.get_current_object_select();
    let isModified = currentObjectSelect.attr('data-is-modified') == '1';

    let requestText = $('#data-request').val();
    $.fn.zato.ide.save_request_to_history(requestText);

    let invokeFunc = function() {
        const options = {
            'request_form_id': '#invoke-service-request-form',
            'on_started_activate_blinking': ['#invoking-please-wait'],
            'on_ended_draw_attention': ['#result-header'],
            'get_request_url_func': $.fn.zato.invoker.get_sync_invoke_request_url,
            'is_invoke': true,
        };
        $.fn.zato.invoker.run_sync_invoker(options);
    };

    if (isModified) {
        $.fn.zato.ide.run_sync_deployer(invokeFunc);
    }
    else {
        invokeFunc();
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.invoke = function(
    url,
    data,
    callback,
    dataType,
    context
) {
    dataType = dataType || 'JSON';
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        complete: callback,
        dataType: dataType,
        context: context
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.submit_form = function(
    url,
    formId,
    options,
    onSuccessFunc,
    onErrorFunc,
    displayTimeout,
    dataFormat,
) {

    let timeout = displayTimeout || 120;
    let form = $(formId);
    let formData = form.serialize();

    $.ajax({
        type: 'POST',
        url: url,
        data: formData,
        dataType: dataFormat,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        async: true,

        success: function(data, textStatus, request) {
            let onSuccess = function() {
                onSuccessFunc(options, data);
            }
            setTimeout(onSuccess, timeout)
        },

        error: function(jqXHR, textStatus, errorMessage) {
            let onError = function() {
                onErrorFunc(options, jqXHR, textStatus, errorMessage);
            }
            setTimeout(onError, timeout)
        },

    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.get_sync_invoke_request_url = function() {
    let select = $('#object-select :selected');
    let service = select.attr('data-service-name');

    let out = '/zato/service/invoke/' + service + '/cluster/1/';
    return out
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.draw_attention = function(elemList) {
    elemList.each(function(element) {
        let wrappedElement = $(element);
        wrappedElement.removeClass('hidden');
        wrappedElement.removeClass('invoker-draw-attention');
        wrappedElement.addClass('invoker-draw-attention', 1);
    });

};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.format_error_traceback = function(responseData) {

    const responseString = JSON.stringify(responseData);

    let hasErrorMarker = responseString.indexOf('··· Error ···') !== -1;

    if (!hasErrorMarker) {
        return responseData;
    }

    let formatted = responseString;
    formatted = formatted.replace(/^\["/, '');
    formatted = formatted.replace(/"\]$/, '');
    formatted = formatted.replace(/\\n/g, '\n');
    formatted = formatted.replace(/\\"/g, '\"');
    formatted = formatted.replace(/\\\\/g, '\\');

    return formatted;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.on_form_ended_common_impl = function(
    options,
    status,
    response,
) {

    let hasResponse = !!response.data;
    let onStartedActivateBlinking = options['on_started_activate_blinking'];
    let onEndedDrawAttention = options['on_ended_draw_attention'];

    // Disable blinking for all the elements that should blink
    onStartedActivateBlinking.each(function(element) {
        $.fn.zato.toggle_css_class($(element), 'invoker-blinking', 'hidden');
    });

    // End by draw attention to specific elements
    $.fn.zato.invoker.draw_attention(onEndedDrawAttention);

    // This is optional
    if(response.response_time_human && response.response_time_human != 'default') {
        status += ' | ';
        status += response.response_time_human;
    }

    if(hasResponse) {
        if($.fn.zato.is_object(response.data)) {
            responseData = response.data;
        }
        else {
            responseData = response.data;
        }

        let isArrayWithSingleString = Array.isArray(responseData);
        if (isArrayWithSingleString) {
            if (responseData.length === 1) {
                if (typeof responseData[0] === 'string') {
                    responseData = responseData[0];
                }
            }
        }

    }
    else {
        responseData = $.fn.zato.to_json(response.data[0].zato_env);
    }

    $('#result-header').text(status);

    const formattedResponse = $.fn.zato.invoker.format_error_traceback(responseData);

    if (typeof formattedResponse === 'string') {
        $('#data-response').text(formattedResponse);
    }
    else {
        $('#data-response').text(JSON.stringify(formattedResponse));
    }

    let requestText = $('#data-request').val();
    let responseText = $('#data-response').val();
    if ($.fn.zato.ide && $.fn.zato.ide.save_request_to_history && options.is_invoke) {
        $.fn.zato.ide.save_request_to_history(requestText, responseText);
    }

    if (window.zato && window.zato.updateMessageViewer) {
        window.zato.updateMessageViewer(responseText);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.on_form_ended_common = function(
    options,
    status,
    data,
) {

    if($.fn.zato.is_object(data)) {
        var response = data;
    }
    else {
        var response = $.parseJSON(data);
    }

    $.fn.zato.invoker.on_form_ended_common_impl(options, status, response)

};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.on_sync_invoke_ended_error = function(options, jqXHR, textStatus, errorMessage) {

    let status = jqXHR.status + ' ' + errorMessage;
    $.fn.zato.invoker.on_form_ended_common(options, status, jqXHR.responseText);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.on_sync_invoke_ended_success = function(options, data) {

    let status = '200 OK';
    let onPostSuccessFunc = options['on_post_success_func'];

    $.fn.zato.invoker.on_form_ended_common(options, status, data);

    if(onPostSuccessFunc) {
        onPostSuccessFunc();
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.run_sync_form_submitter = function(options) {

    // Local variables
    let requestFormId = options['request_form_id'];
    let getRequestUrlFunc = options['get_request_url_func'];
    let onStartedActivateBlinking = options['on_started_activate_blinking'];
    let onEndedDrawAttention = options['on_ended_draw_attention'];

    // Obtain the URL we are to invoke
    let url = getRequestUrlFunc();

    // Enable blinking for all the elements that should blink
    onStartedActivateBlinking.each(function(element) {
        $.fn.zato.toggle_css_class($(element), 'hidden', 'invoker-blinking');
    });

    // Disable all the elements that previously might have needed attention
    onEndedDrawAttention.each(function(element) {
        let wrappedElement = $(element);
        wrappedElement.addClass('hidden');
    });

    // Submit the form, if we have one on input
    if(requestFormId) {
        $.fn.zato.invoker.submit_form(
            url,
            requestFormId,
            options,
            $.fn.zato.invoker.on_sync_invoke_ended_success,
            $.fn.zato.invoker.on_sync_invoke_ended_error
        )
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.run_sync_invoker = function(options) {
    $.fn.zato.invoker.run_sync_form_submitter(options);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Shared history functions (used by both IDE and channel/outconn invoker)
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.get_history = function(key) {
    let historyJSON = localStorage.getItem(key);
    if (historyJSON) {
        return JSON.parse(historyJSON);
    }
    return [];
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.save_to_history = function(key, requestText, responseText) {
    if (!requestText) {
        requestText = '';
    }

    let history = $.fn.zato.invoker.get_history(key);

    history.unshift({
        text: requestText,
        response: responseText || '',
        timestamp: Date.now()
    });

    if (history.length > 200) {
        history = history.slice(0, 200);
    }

    localStorage.setItem(key, JSON.stringify(history));
    return history;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.delete_history_item = function(key, index) {
    let history = $.fn.zato.invoker.get_history(key);
    history.splice(index, 1);
    localStorage.setItem(key, JSON.stringify(history));
    return history;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.filter_history = function(key, searchText) {
    let history = $.fn.zato.invoker.get_history(key);

    if (!searchText || searchText.trim() === '') {
        return {history: history, isSearchResult: false};
    }

    let filtered = history.filter(function(item) {
        let text = typeof item === 'string' ? item : item.text;
        return text.toLowerCase().indexOf(searchText.toLowerCase()) !== -1;
    });

    return {history: filtered, isSearchResult: true};
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.format_timestamp = function(timestamp) {
    let now = new Date();
    let then = new Date(timestamp);
    let diffMs = now - then;
    let diffSec = Math.floor(diffMs / 1000);
    let diffMin = Math.floor(diffSec / 60);
    let diffHour = Math.floor(diffMin / 60);
    let diffDay = Math.floor(diffHour / 24);

    let timeString = then.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });

    if (diffSec < 60) {
        if (diffSec === 0) diffSec = 1;
        return diffSec === 1 ? '1 second ago' : diffSec + ' seconds ago';
    }
    else if (diffMin < 60) {
        return diffMin === 1 ? '1 minute ago' : diffMin + ' minutes ago';
    }
    else if (diffHour < 24) {
        return diffHour === 1 ? '1 hour ago' : diffHour + ' hours ago';
    }
    else if (diffDay === 1) {
        return 'yesterday at ' + timeString;
    }
    else if (diffDay < 7) {
        return diffDay + ' days ago at ' + timeString;
    }
    else if (diffDay < 14) {
        let dayName = then.toLocaleDateString('en-US', { weekday: 'long' });
        return dayName + ', last week at ' + timeString;
    }
    else if (diffDay < 21) {
        let dayName = then.toLocaleDateString('en-US', { weekday: 'long' });
        return dayName + ', two weeks ago at ' + timeString;
    }
    else if (diffDay < 60) {
        return 'a month ago at ' + timeString;
    }
    else if (diffDay < 365) {
        let months = Math.floor(diffDay / 30);
        return months === 1 ? 'a month ago at ' + timeString : months + ' months ago at ' + timeString;
    }
    else {
        let years = Math.floor(diffDay / 365);
        return years === 1 ? 'a year ago at ' + timeString : years + ' years ago at ' + timeString;
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.format_json = function(text) {
    if (!text || typeof text !== 'string') {
        return text || '';
    }
    let trimmed = text.trim();
    let startsWithBrace = trimmed.startsWith('{');
    let endsWithBrace = trimmed.endsWith('}');
    let startsWithBracket = trimmed.startsWith('[');
    let endsWithBracket = trimmed.endsWith(']');
    let isObject = startsWithBrace && endsWithBrace;
    let isArray = startsWithBracket && endsWithBracket;

    if (isObject || isArray) {
        try {
            return JSON.stringify(JSON.parse(trimmed), null, 2);
        }
        catch (event) {
            return text;
        }
    }
    return text;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.populate_history_list = function(listContainer, history, isSearchResult, callbacks) {
    listContainer.empty();

    if (!history || history.length === 0) {
        let message = isSearchResult ? 'No results' : 'Nothing in history';
        listContainer.append('<div class="invoker-history-empty">' + message + '</div>');
        return;
    }

    for (let historyIdx = 0; historyIdx < history.length; historyIdx++) {
        $.fn.zato.invoker._render_history_item(listContainer, history, historyIdx, callbacks);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._highlight_history_items = function(listContainer, highlightLexer) {
    var pendingItems = listContainer.find('.invoker-history-item-text');
    var batchSize = 20;
    var processed = 0;

    pendingItems.each(function() {
        var element = $(this);
        var isPending = element.data('highlightPending');
        if (!isPending) {
            return;
        }

        processed++;
        if (processed > batchSize) {
            return false;
        }

        element.data('highlightPending', false);
        var text = this.textContent;

        $.fn.zato.highlightElement(element, text, highlightLexer);
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._render_history_item = function(listContainer, history, historyIdx, callbacks) {
    let item = history[historyIdx];
    let requestText = typeof item === 'string' ? item : item.text;
    let timestamp = typeof item === 'string' ? null : item.timestamp;
    let response = typeof item === 'string' ? '' : item.response;
    if (response === null) {
        response = '';
    }

    let trimmedResponse = response.trim();
    let hasResponse = !!trimmedResponse;
    if (trimmedResponse === '(None)') {
        hasResponse = false;
    }

    let wrapper = $('<div class="invoker-history-item-wrapper"></div>');
    wrapper.attr('data-index', historyIdx);

    let numberBox = $('<div class="invoker-history-item-number"></div>').text(historyIdx + 1);
    let textBox = $('<div class="invoker-history-item-text syntax-monokai"></div>');

    let rawText = requestText;
    if (!rawText) {
        rawText = '(No request)';
    }
    else if (rawText.trim() === '') {
        rawText = '(No request)';
    }

    textBox.text(rawText);
    textBox.data('highlightPending', true);

    let showResponseLabel = hasResponse ? 'Show response' : '(No response)';
    let showResponseBox = $('<div class="invoker-history-item-show-response"></div>');
    showResponseBox.text(showResponseLabel);

    let timestampBox = $('<div class="invoker-history-item-timestamp"></div>');
    if (timestamp) {
        timestampBox.text($.fn.zato.invoker.format_timestamp(timestamp));
    }

    let deleteBox = $('<div class="invoker-history-item-delete"></div>').text('\u2715');

    let onSelect = function() {
        if (callbacks && callbacks.on_select) {
            callbacks.on_select($(this).closest('.invoker-history-item-wrapper').attr('data-index'));
        }
    };
    textBox.on('click', onSelect);
    numberBox.on('click', onSelect);
    timestampBox.on('click', onSelect);

    showResponseBox.on('click', function(event) {
        event.stopPropagation();
        $.fn.zato.invoker._toggle_response_detail(wrapper, historyIdx, item);
    });

    deleteBox.on('click', function(event) {
        event.stopPropagation();
        if (callbacks && callbacks.on_delete) {
            callbacks.on_delete($(this).closest('.invoker-history-item-wrapper').attr('data-index'));
        }
    });

    wrapper.append(numberBox, textBox, showResponseBox, timestampBox, deleteBox);
    listContainer.append(wrapper);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._toggle_response_detail = function(wrapper, index, item) {
    let detailId = 'invoker-history-response-detail-' + index;
    let existingDetail = $('#' + detailId);

    if (existingDetail.length > 0) {
        existingDetail.toggleClass('visible');
        return;
    }

    let response = typeof item === 'string' ? '' : item.response;
    if (response === null) {
        response = '';
    }
    let detail = $('<div class="invoker-history-response-detail visible" id="' + detailId + '"></div>');

    let header = $('<div class="invoker-history-response-detail-header"></div>');
    let title = $('<div class="invoker-history-response-detail-title">Response</div>');
    let copyButton = $('<button class="invoker-history-response-detail-copy">Copy</button>');

    copyButton.on('click', function(event) {
        event.stopPropagation();
        let trimmedResponse = response.trim();
        if (!trimmedResponse) {
            return;
        }
        if (trimmedResponse === '(None)') {
            return;
        }
        navigator.clipboard.writeText(response).catch(function() {});
    });

    header.append(title, copyButton);

    let content = $('<div class="invoker-history-response-detail-content"></div>');
    let trimmedResponse = response.trim();
    let isEmpty = !trimmedResponse;
    if (trimmedResponse === '(None)') {
        isEmpty = true;
    }

    if (isEmpty) {
        content.text('(No response)');
    }
    else {
        $.fn.zato.highlight_response(content, response);
    }

    detail.append(header, content);
    wrapper.after(detail);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.on_history_up = function(key, textareaSelector, currentIndex) {
    let history = $.fn.zato.invoker.get_history(key);
    if (history.length === 0) {
        return currentIndex;
    }

    if (typeof currentIndex !== 'number') {
        currentIndex = -1;
    }

    let textareaValue = $(textareaSelector).val();
    let newIndex = currentIndex + 1;

    if (currentIndex === -1 && history.length > 0) {
        let firstText = typeof history[0] === 'string' ? history[0] : history[0].text;
        if (textareaValue === firstText) {
            newIndex = 1;
        }
    }

    if (newIndex >= history.length) {
        return currentIndex;
    }

    let item = history[newIndex];
    $(textareaSelector).val(typeof item === 'string' ? item : item.text);
    return newIndex;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.on_history_down = function(key, textareaSelector, currentIndex) {
    let history = $.fn.zato.invoker.get_history(key);
    if (history.length === 0) {
        return currentIndex;
    }

    if (typeof currentIndex !== 'number') {
        currentIndex = -1;
    }

    let newIndex = currentIndex - 1;

    if (newIndex < -1) {
        return currentIndex;
    }

    if (newIndex === -1) {
        $(textareaSelector).val('');
    }
    else {
        let item = history[newIndex];
        $(textareaSelector).val(typeof item === 'string' ? item : item.text);
    }
    return newIndex;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Invoker modal overlay (channel / outconn)
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._modal_config = null;

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.render_overlay_html = function() {
    if ($('#invoker-modal-overlay').length > 0) {
        return;
    }

    let html = ''
        + '<div id="invoker-modal-overlay" class="invoker-modal-overlay hidden">'
        +   '<div class="invoker-modal-backdrop"></div>'
        +   '<div class="invoker-modal-content">'
        +     '<div class="invoker-modal-header">'
        +       '<h2 id="invoker-modal-title">Invoke</h2>'
        +       '<button class="invoker-modal-close-btn" id="invoker-modal-close">\u2715</button>'
        +     '</div>'
        +     '<div class="invoker-modal-body">'
        +       '<form id="invoker-modal-form" novalidate>'
        +         '<textarea id="invoker-modal-request" class="invoker-modal-request-textarea" name="data-request"'
        +           ' placeholder="Enter JSON or key=value pairs, e.g.:\nkey1=value1\nkey2=value2\n\nCtrl+\u2191/\u2193 for history, Ctrl+K for full history"></textarea>'
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

    $('body').append(html);
    $.fn.zato.invoker._bind_modal_events();
    $.fn.zato.invoker._make_draggable('.invoker-modal-header', '.invoker-modal-content');

    let historyHTML = ''
        + '<div id="invoker-modal-history-overlay" class="invoker-history-overlay hidden">'
        +   '<div class="invoker-history-overlay-backdrop"></div>'
        +   '<div class="invoker-history-overlay-content">'
        +     '<div class="invoker-history-overlay-header">'
        +       '<h2>Invocation history</h2>'
        +       '<button class="invoker-history-close-btn" id="invoker-modal-history-close">\u2715</button>'
        +     '</div>'
        +     '<div class="invoker-history-overlay-search">'
        +       '<input type="text" id="invoker-modal-history-search" placeholder="Search history..." />'
        +     '</div>'
        +     '<div class="invoker-history-overlay-list" id="invoker-modal-history-list"></div>'
        +   '</div>'
        + '</div>';

    $('body').append(historyHTML);
    $.fn.zato.invoker._bind_history_events();
    $.fn.zato.invoker._make_draggable('.invoker-history-overlay-header', '.invoker-history-overlay-content');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._bind_modal_events = function() {
    $('#invoker-modal-close').on('click', $.fn.zato.invoker.close_overlay);
    $('.invoker-modal-backdrop').on('click', $.fn.zato.invoker.close_overlay);
    $('#invoker-modal-invoke-btn').on('click', $.fn.zato.invoker._on_modal_invoke);
    $('#invoker-modal-history-btn').on('click', $.fn.zato.invoker._open_modal_history);
    $('#invoker-modal-copy-btn').on('click', $.fn.zato.invoker._on_copy_response);


    $('#invoker-modal-request').on('keydown', function(event) {
        let isCtrl = event.ctrlKey || event.metaKey;
        if (isCtrl && event.key === 'Enter') {
            event.preventDefault();
            $.fn.zato.invoker._on_modal_invoke();
        }
        else if (isCtrl && event.key === 'ArrowUp') {
            event.preventDefault();
            $.fn.zato.invoker._on_modal_history_up();
        }
        else if (isCtrl && event.key === 'ArrowDown') {
            event.preventDefault();
            $.fn.zato.invoker._on_modal_history_down();
        }
        else if (isCtrl && event.key.toLowerCase() === 'k') {
            event.preventDefault();
            $.fn.zato.invoker._open_modal_history();
        }
    });

    $(document).on('keydown.invoker_modal', function(event) {
        if (event.key !== 'Escape') {
            return;
        }
        let historyOverlay = $('#invoker-modal-history-overlay');
        if (!historyOverlay.hasClass('hidden')) {
            event.preventDefault();
            $.fn.zato.invoker._close_modal_history();
            return;
        }
        let modalOverlay = $('#invoker-modal-overlay');
        if (!modalOverlay.hasClass('hidden')) {
            event.preventDefault();
            $.fn.zato.invoker.close_overlay();
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._bind_history_events = function() {
    $('#invoker-modal-history-close').on('click', $.fn.zato.invoker._close_modal_history);
    $('#invoker-modal-history-overlay .invoker-history-overlay-backdrop').on('click', $.fn.zato.invoker._close_modal_history);

    $('#invoker-modal-history-search').on('input', function() {
        let config = $.fn.zato.invoker._modal_config;
        if (!config) return;
        let result = $.fn.zato.invoker.filter_history(config.history_key, $(this).val());
        var list = $('#invoker-modal-history-list');
        $.fn.zato.invoker.populate_history_list(
            list,
            result.history,
            result.isSearchResult,
            $.fn.zato.invoker._get_modal_history_callbacks()
        );
        let lexer = config.highlight_lexer || '';
        $.fn.zato.invoker._highlight_history_items(list, lexer);
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._get_history_key = function() {
    let config = $.fn.zato.invoker._modal_config;
    return config ? config.history_key : null;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._get_modal_history_callbacks = function() {
    return {
        on_select: function(index) {
            let config = $.fn.zato.invoker._modal_config;
            if (!config) return;
            let history = $.fn.zato.invoker.get_history(config.history_key);
            let item = history[index];
            let requestText = typeof item === 'string' ? item : item.text;
            $('#invoker-modal-request').val(requestText);
            window.zato_invoker_history_index = parseInt(index);
            $.fn.zato.invoker._close_modal_history();
            $('#invoker-modal-request').focus();
        },
        on_delete: function(index) {
            let config = $.fn.zato.invoker._modal_config;
            if (!config) return;
            let history = $.fn.zato.invoker.delete_history_item(config.history_key, index);
            $.fn.zato.invoker.populate_history_list(
                $('#invoker-modal-history-list'),
                history,
                false,
                $.fn.zato.invoker._get_modal_history_callbacks()
            );
        }
    };
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.toggle_more_options = function() {
    $('#invoker-more-options').toggleClass('hidden');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.open_overlay = function(config) {
    $.fn.zato.invoker.render_overlay_html();
    $.fn.zato.invoker._modal_config = config;
    window.zato_invoker_history_index = -1;

    $('#invoker-modal-title').text('Invoke: ' + config.name);

    let saved = $.fn.zato.invoker._load_overlay_state(config.history_key);
    let content = $('.invoker-modal-content');

    if (saved.width && saved.height) {
        content.css({'width': saved.width, 'height': saved.height});
    }
    else {
        content.css({'width': '', 'height': ''});
    }

    if (saved.left && saved.top) {
        content.css({'position': 'fixed', 'left': saved.left, 'top': saved.top, 'margin': '0', 'transform': 'none'});
    }
    else {
        content.css({'position': '', 'left': '', 'top': '', 'margin': '', 'transform': ''});
    }

    let requestValue = saved.request || '';
    $('#invoker-modal-request').val(requestValue);
    $('#invoker-modal-method').val(saved.method || 'POST');
    $('#invoker-modal-query-params').val(saved.query_params || '');
    $('#invoker-modal-path-params').val(saved.path_params || '');
    $('#invoker-modal-status').text(saved.status || '');

    if (saved.response_raw) {
        let pre = $('#invoker-modal-response');
        pre.data('raw-response', saved.response_raw);
        $.fn.zato.highlight_response(pre, saved.response_raw);
    }
    else {
        $('#invoker-modal-response').text('').removeData('raw-response');
        $('#invoker-modal-response-gutter').text('');
    }

    if (saved.more_options_open) {
        $('#invoker-more-options').removeClass('hidden');
    }
    else {
        $('#invoker-more-options').addClass('hidden');
    }

    $('#invoker-modal-overlay').removeClass('hidden');
    $('#invoker-modal-request').focus();
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.close_overlay = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (config) {
        $.fn.zato.invoker._save_overlay_state(config.history_key);
    }
    $('#invoker-modal-overlay').addClass('hidden');
    $.fn.zato.invoker._modal_config = null;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._save_overlay_state = function(historyKey) {
    let content = $('.invoker-modal-content');
    let rect = content[0].getBoundingClientRect();
    let widthValue = content[0].style.width || (rect.width + 'px');
    let heightValue = content[0].style.height || (rect.height + 'px');
    let leftValue = content[0].style.left || '';
    let topValue = content[0].style.top || '';

    let state = {
        width: widthValue,
        height: heightValue,
        left: leftValue,
        top: topValue,
        request: $('#invoker-modal-request').val() || '',
        method: $('#invoker-modal-method').val() || 'POST',
        query_params: $('#invoker-modal-query-params').val() || '',
        path_params: $('#invoker-modal-path-params').val() || '',
        variables: $('#invoker-modal-variables').val() || '',
        response_raw: $('#invoker-modal-response').data('raw-response') || '',
        status: $('#invoker-modal-status').text() || '',
        more_options_open: !$('#invoker-more-options').hasClass('hidden')
    };
    localStorage.setItem('zato_invoker_state_' + historyKey, JSON.stringify(state));
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._load_overlay_state = function(historyKey) {
    let raw = localStorage.getItem('zato_invoker_state_' + historyKey);
    if (raw) {
        try {
            return JSON.parse(raw);
        }
        catch (event) {}
    }
    return {};
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker.collect_form_data = function() {
    let data = {
        'data-request': $('#invoker-modal-request').val() || '',
        'request_method': $('#invoker-modal-method').val() || 'POST',
        'query_params': $('#invoker-modal-query-params').val() || '',
        'path_params': $('#invoker-modal-path-params').val() || ''
    };
    return data;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._on_modal_invoke = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (!config) return;

    let collectFunc = config.collect_form_data_func || $.fn.zato.invoker.collect_form_data;
    let formData = collectFunc();
    let url = config.get_invoke_url_func(config.id);

    $.fn.zato.invoker.save_to_history(config.history_key, formData['data-request']);
    $.fn.zato.invoker._set_modal_invoking();

    $.ajax({
        type: 'POST',
        url: url,
        data: formData,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function(data) {
            $.fn.zato.invoker._on_modal_invoke_success(data, formData['data-request']);
        },
        error: function(jqXHR, textStatus, errorMessage) {
            $.fn.zato.invoker._on_modal_invoke_error(jqXHR, formData['data-request']);
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._set_modal_invoking = function() {
    $('#invoker-modal-status').text('Invoking ...').addClass('invoker-blinking');
    $('#invoker-modal-response').text('').removeData('raw-response');
    $('#invoker-modal-response-gutter').text('');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._on_modal_invoke_success = function(data, requestText) {
    let response = typeof data === 'string' ? JSON.parse(data) : data;
    let status = '200 OK';

    if (response.response_time_human) {
        status += ' | ' + response.response_time_human;
    }

    let responseText = '';
    if (response.data !== undefined && response.data !== null) {
        responseText = typeof response.data === 'string' ? response.data : JSON.stringify(response.data, null, 2);
    }

    $.fn.zato.invoker._set_modal_result(status, responseText, requestText);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._on_modal_invoke_error = function(jqXHR, requestText) {
    let status = jqXHR.status + ' ' + (jqXHR.statusText || 'Error');
    let responseText = jqXHR.responseText || '';

    try {
        let parsed = JSON.parse(responseText);
        if (parsed.data !== undefined) {
            responseText = typeof parsed.data === 'string' ? parsed.data : JSON.stringify(parsed.data, null, 2);
        }
        if (parsed.response_time_human) {
            status += ' | ' + parsed.response_time_human;
        }
    }
    catch (event) {
        // responseText is not JSON, use as-is
    }

    $.fn.zato.invoker._set_modal_result(status, responseText, requestText);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._set_modal_result = function(status, responseText, requestText) {
    $('#invoker-modal-status').text(status).removeClass('invoker-blinking');

    let formatted = $.fn.zato.invoker._format_response_text(responseText);
    let pre = $('#invoker-modal-response');
    pre.data('raw-response', formatted);
    $.fn.zato.highlight_response(pre, formatted);

    let config = $.fn.zato.invoker._modal_config;
    if (config) {
        $.fn.zato.invoker.save_to_history(config.history_key, requestText, responseText);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._on_format_response = function() {
    let pre = $('#invoker-modal-response');
    let raw = pre.data('raw-response') || pre.text() || '';
    let formatted = $.fn.zato.invoker._format_response_text(raw);
    pre.data('raw-response', formatted);
    $.fn.zato.highlight_response(pre, formatted);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._format_response_text = function(text) {
    if (!text || typeof text !== 'string') {
        return text || '';
    }
    let trimmed = text.trim();

    let startsWithBrace = trimmed.startsWith('{');
    let endsWithBrace = trimmed.endsWith('}');
    let startsWithBracket = trimmed.startsWith('[');
    let endsWithBracket = trimmed.endsWith(']');
    let isObject = startsWithBrace && endsWithBrace;
    let isArray = startsWithBracket && endsWithBracket;

    if (isObject || isArray) {
        try {
            return JSON.stringify(JSON.parse(trimmed), null, 2);
        }
        catch (event) {}
    }

    let isXml = trimmed.startsWith('<');
    if (isXml) {
        if (trimmed.endsWith('>')) {
            return $.fn.zato.invoker._format_xml(trimmed);
        }
    }

    return text;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._format_xml = function(xmlText) {
    let indent = 0;
    let lines = [];
    let tokens = xmlText.replace(/>\s*</g, '>\n<').split('\n');

    for (let tokenIdx = 0; tokenIdx < tokens.length; tokenIdx++) {
        let token = tokens[tokenIdx].trim();
        if (!token) {
            continue;
        }
        let isClosing = token.startsWith('</');
        let isSelfClosing = token.endsWith('/>') || token.startsWith('<?');

        if (isClosing) {
            indent = Math.max(0, indent - 1);
        }

        lines.push('  '.repeat(indent) + token);

        if (!isClosing && !isSelfClosing) {
            indent++;
        }
    }

    let out = lines.join('\n');
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._update_line_numbers = function(preElement) {
    $.fn.zato.update_response_line_numbers(preElement);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._on_copy_response = function() {
    let pre = $('#invoker-modal-response');
    let raw = pre.data('raw-response') || pre.text() || '';
    if (!raw.trim()) {
        return;
    }

    let link = $('#invoker-modal-copy-btn');
    navigator.clipboard.writeText(raw).then(function() {
        $.fn.zato.invoker._show_copied_tooltip(link);
    }).catch(function() {});
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._show_copied_tooltip = function(anchorElement) {
    let offset = anchorElement.offset();
    let tooltip = $('<span class="invoker-copied-tooltip">Copied to clipboard</span>');
    let topPosition = (offset.top - $(window).scrollTop() + anchorElement.outerHeight() / 2 - 10) + 'px';
    let leftPosition = (offset.left + anchorElement.outerWidth() + 8) + 'px';
    tooltip.css({
        'position': 'fixed',
        'top': topPosition,
        'left': leftPosition
    });
    $('body').append(tooltip);
    setTimeout(function() {
        tooltip.remove();
    }, 600);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._make_draggable = function(headerSelector, contentSelector) {
    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    $(headerSelector).on('mousedown', function(event) {
        if ($(event.target).is('button, input, a')) {
            return;
        }
        isDragging = true;
        let content = $(contentSelector);
        let rect = content[0].getBoundingClientRect();
        offsetX = event.clientX - rect.left;
        offsetY = event.clientY - rect.top;

        content.css('position', 'fixed');
        content.css('margin', '0');
        content.css('left', rect.left + 'px');
        content.css('top', rect.top + 'px');
        content.css('transform', 'none');
        event.preventDefault();
    });

    $(document).on('mousemove', function(event) {
        if (!isDragging) {
            return;
        }
        let content = $(contentSelector);
        content.css('left', (event.clientX - offsetX) + 'px');
        content.css('top', (event.clientY - offsetY) + 'px');
    });

    $(document).on('mouseup', function() {
        isDragging = false;
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._on_modal_history_up = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (!config) return;
    window.zato_invoker_history_index = $.fn.zato.invoker.on_history_up(
        config.history_key, '#invoker-modal-request', window.zato_invoker_history_index);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._on_modal_history_down = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (!config) return;
    window.zato_invoker_history_index = $.fn.zato.invoker.on_history_down(
        config.history_key, '#invoker-modal-request', window.zato_invoker_history_index);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._open_modal_history = function() {
    let config = $.fn.zato.invoker._modal_config;
    if (!config) return;

    let history = $.fn.zato.invoker.get_history(config.history_key);
    $.fn.zato.invoker.populate_history_list(
        $('#invoker-modal-history-list'),
        history,
        false,
        $.fn.zato.invoker._get_modal_history_callbacks()
    );

    $('.invoker-history-overlay-content').css({'position': '', 'left': '', 'top': '', 'margin': '', 'transform': ''});
    $('#invoker-modal-history-overlay').removeClass('hidden');
    $('#invoker-modal-history-search').val('').focus();

    // Trigger highlighting now that the overlay is visible
    let lexer = config.highlight_lexer || '';
    $.fn.zato.invoker._highlight_history_items($('#invoker-modal-history-list'), lexer);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.invoker._close_modal_history = function() {
    $('#invoker-modal-history-overlay').addClass('hidden');
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
