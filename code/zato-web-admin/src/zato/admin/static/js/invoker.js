
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$(document).ready(function() {
    $('#invoke-service').click($.fn.zato.invoker.on_invoke_submitted);
});

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_invoke_submitted = function() {

    const options = {
        "form_id": "#invoke-service-form",
        "on_started_activate_blinking": ["#invoking-please-wait"],
        "on_started_remove_hidden": ["#result-header-separator"],
        "on_ended_draw_attention": ["#result-header"],
    }
    $.fn.zato.invoker.run_sync_invoker(options);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.invoke = function(
    url,
    data,
    callback,
    data_type,
    context
) {
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

$.fn.zato.invoker.run_sync_invoker = function(options) {

    console.log("Options 1: " +  Object.entries(options));

    // Local variables
    let form_id = options["form_id"];
    let on_started_activate_blinking = options["on_started_activate_blinking"];
    let on_started_remove_hidden = options["on_started_remove_hidden"];
    let on_ended_draw_attention = options["on_ended_draw_attention"];

    // Show elements that by default were hidden
    on_started_remove_hidden.each(function(elem) {
        $(elem).removeClass("hidden");
    });

    // Enable blinking for all the elements that should blink
    on_started_activate_blinking.each(function(elem) {
        $.fn.zato.toggle_css_class($(elem), "hidden", "invoker-blinking");
    });

    // Submit the form, if we have one on input
    if(form_id) {
        let form = $(form_id);
        let form_data = new FormData(form[0]);

        $.ajax({
            type: "POST",
            url: "address",// where you wanna post
            data: form_data,
            processData: false,
            contentType: false,
            error: function(jqXHR, text_status, error_message) {
                console.log(error_message);
            },
            success: function(data) {console.log(data)}
        });

    }

    // End by draw attention to specific elements
    on_ended_draw_attention2.each(function(elem) {
        let _elem = $(elem);
        _elem.removeClass("hidden");
        _elem.removeClass("invoker-draw-attention");
        _elem.addClass("invoker-draw-attention", 1);
    });

    /*

    var _callback = function(data, status, xhr){
        var success = status == 'success';
        if(success) {
            let action_verb = $('#action_verb').val() || 'action-verb-html-js';
            $.fn.zato.user_message(true, 'OK, '+ action_verb +' successfully');
            $('#response_data').text(JSON.stringify(data) || '(No response)');
        }
        else {
            $.fn.zato.user_message(false, 'Invocation error -> `' + status + '`');
            $('#response_data').text(data.responseText);
        }
    }

    var options = {
        success: _callback,
        error:  _callback,
        resetForm: false,
        'dataType': 'json',
    };

    form.ajaxSubmit(options);
    return false;
    */

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

/*
$(document).ready(function() {

    var _callback = function(data, status, xhr){
        var success = status == 'success';
        var msg = success ? data : data.responseText;
        $.fn.zato.user_message(success, msg);
    }

    var options = {
        success: _callback,
        error:  _callback,
        resetForm: false,
    };

    $('#invoke_service_form').submit(function() {
        $(this).ajaxSubmit(options);
        return false;
    });
});
*/
