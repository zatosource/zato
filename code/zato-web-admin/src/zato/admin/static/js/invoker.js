/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_invoke_submitted = function() {
    console.log("on_invoke_submitted: START");
    let current_object_select = $.fn.zato.ide.get_current_object_select();
    let is_modified = current_object_select.attr('data-is-modified') == '1';
    console.log("on_invoke_submitted: is_modified:", is_modified);

    let invoke_func = function() {
        console.log("on_invoke_submitted: invoke_func called");
        const options = {
            "request_form_id": "#invoke-service-request-form",
            "on_started_activate_blinking": ["#invoking-please-wait"],
            "on_ended_draw_attention": ["#result-header"],
            "get_request_url_func": $.fn.zato.invoker.get_sync_invoke_request_url,
        };
        $.fn.zato.invoker.run_sync_invoker(options);
    };

    if (is_modified) {
        console.log("on_invoke_submitted: deploying first");
        $.fn.zato.ide.run_sync_deployer(invoke_func);
    } else {
        console.log("on_invoke_submitted: invoking directly");
        invoke_func();
    }
};

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.invoke = function(
    url,
    data,
    callback,
    data_type,
    context
) {
    console.log("invoke: called with url:", url);
    console.log("invoke: data:", data);
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
    console.log("submit_form: CALLED with url:", url);
    console.log("submit_form: form_id:", form_id);
    console.log("submit_form: data_format:", data_format);
    
    let _display_timeout = display_timeout || 120;
    let form = $(form_id);
    let form_data = form.serialize();
    let _data_format = data_format || null;

    console.log("submit_form: form_data:", form_data);
    console.log("submit_form: _display_timeout:", _display_timeout);

    $.ajax({
        type: "POST",
        url: url,
        data: form_data,
        dataType: data_format,
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        async: false,

        success: function(data, text_status, request) {
            console.log("submit_form: success callback triggered");
            console.log("submit_form: data:", data);
            console.log("submit_form: text_status:", text_status);
            console.log("submit_form: request.status:", request.status);
            let _on_success = function() {
                on_success_func(options, data);
            }
            setTimeout(_on_success, _display_timeout)
        },

        error: function(jq_xhr, text_status, error_message) {
            console.log("submit_form: error callback triggered");
            console.log("submit_form: jq_xhr.status:", jq_xhr.status);
            console.log("submit_form: jq_xhr.responseText:", jq_xhr.responseText);
            console.log("submit_form: text_status:", text_status);
            console.log("submit_form: error_message:", error_message);
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
    console.log("get_sync_invoke_request_url: select:", JSON.stringify(select));
    console.log("get_sync_invoke_request_url: service:", JSON.stringify(service));
    let out = "/zato/service/invoke/"+ service + "/cluster/1/";
    console.log("get_sync_invoke_request_url: out:", JSON.stringify(out));
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
    console.log("format_error_traceback: input response_data type:", typeof response_data);
    console.log("format_error_traceback: input response_data:", response_data);
    
    const response_str = JSON.stringify(response_data);
    console.log("format_error_traceback: stringified response_str:", response_str);
    console.log("format_error_traceback: response_str length:", response_str.length);
    
    const has_error_marker = response_str.indexOf("··· Error ···") !== -1;
    console.log("format_error_traceback: has_error_marker:", has_error_marker);
    
    if (!has_error_marker) {
        console.log("format_error_traceback: no error marker found, returning original data");
        return response_data;
    }
    
    console.log("format_error_traceback: error marker found, formatting traceback");
    let formatted = response_str;
    console.log("format_error_traceback: before replacements:", formatted.substring(0, 200));
    formatted = formatted.replace(/^\["/, "");
    formatted = formatted.replace(/"\]$/, "");
    formatted = formatted.replace(/\\n/g, "\n");
    formatted = formatted.replace(/\\"/g, "\"");
    formatted = formatted.replace(/\\\\/g, "\\");
    console.log("format_error_traceback: after replacements:", formatted.substring(0, 200));
    console.log("format_error_traceback: final formatted length:", formatted.length);
    
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
            response_data = response.data; //$.fn.zato.to_json(response.data); JSON Parsing and Quotes
        }
        else {
            response_data = response.data;
        }

    }
    else {
        response_data = $.fn.zato.to_json(response.data[0].zato_env);
    }

    console.log("on_form_ended_common_impl: SETTING TEXTAREA NOW");
    $("#result-header").text(status);
    
    console.log("on_form_ended_common_impl: response_data before formatting:", response_data);
    console.log("on_form_ended_common_impl: response_data type:", typeof response_data);
    
    const formatted_response = $.fn.zato.invoker.format_error_traceback(response_data);
    
    console.log("on_form_ended_common_impl: formatted_response:", formatted_response);
    console.log("on_form_ended_common_impl: formatted_response type:", typeof formatted_response);
    console.log("on_form_ended_common_impl: ABOUT TO SET #data-response");
    
    if (typeof formatted_response === "string") {
        console.log("on_form_ended_common_impl: setting text as string");
        $("#data-response").text(formatted_response);
        console.log("on_form_ended_common_impl: DONE setting text as string");
    } else {
        console.log("on_form_ended_common_impl: setting text as JSON.stringify");
        $("#data-response").text(JSON.stringify(formatted_response));
        console.log("on_form_ended_common_impl: DONE setting text as JSON.stringify");
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_form_ended_common = function(
    options,
    status,
    data,
) {

    console.log("on_form_ended_common: data:", data);
    console.log("on_form_ended_common: data type:", typeof data);
    console.log("on_form_ended_common: is_object:", $.fn.zato.is_object(data));
    
    if($.fn.zato.is_object(data)) {
        var response = data;
    }
    else {
        var response = $.parseJSON(data);
    }
    
    console.log("on_form_ended_common: response:", response);
    console.log("on_form_ended_common: response.data:", response.data);
    
    $.fn.zato.invoker.on_form_ended_common_impl(options, status, response)

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_sync_invoke_ended_error = function(options, jq_xhr, text_status, error_message) {

    console.log("on_sync_invoke_ended_error: jq_xhr.responseText:", jq_xhr.responseText);
    console.log("on_sync_invoke_ended_error: jq_xhr.responseText type:", typeof jq_xhr.responseText);
    
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

    console.log("run_sync_form_submitter: called with options:", options);
    
    // Local variables
    let request_form_id = options["request_form_id"];
    let get_request_url_func = options["get_request_url_func"];
    let on_started_activate_blinking = options["on_started_activate_blinking"];
    let on_ended_draw_attention = options["on_ended_draw_attention"];

    console.log("run_sync_form_submitter: request_form_id:", request_form_id);
    
    // Obtain the URL we are to invoke
    let url = get_request_url_func();

    console.log("run_sync_form_submitter: url:", url);
    
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
        console.log("run_sync_form_submitter: submitting form");
        $.fn.zato.invoker.submit_form(
            url,
            request_form_id,
            options,
            $.fn.zato.invoker.on_sync_invoke_ended_success,
            $.fn.zato.invoker.on_sync_invoke_ended_error
        )
    } else {
        console.log("run_sync_form_submitter: no request_form_id, skipping form submission");
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.run_sync_invoker = function(options) {
    console.log("run_sync_invoker: START");
    $.fn.zato.invoker.run_sync_form_submitter(options);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
