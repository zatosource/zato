
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$(document).ready(function() {
    $('#invoke-service').click($.fn.zato.invoker.on_invoke_submitted);
});

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_invoke_submitted = function() {

    const options = {
        "form_id": "#invoke-service-form",
        "on_started_activate_blinking": ["#invoking-please-wait"],
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

$.fn.zato.invoker.on_sync_invoke_ended_error = function(options, jq_xhr, text_status, error_message) {

    // Local variables
    let on_started_activate_blinking = options["on_started_activate_blinking"];
    let on_ended_draw_attention = options["on_ended_draw_attention"];

    // Disable blinking for all the elements that should blink
    on_started_activate_blinking.each(function(elem) {
        $.fn.zato.toggle_css_class($(elem), "invoker-blinking", "hidden");
    });

    // End by draw attention to specific elements
    on_ended_draw_attention.each(function(elem) {
        let _elem = $(elem);
        _elem.removeClass("hidden");
        _elem.removeClass("invoker-draw-attention");
        _elem.addClass("invoker-draw-attention", 1);
    });

    $("#result-header").text("Response 200 OK | 42 ms");

}

$.fn.zato.invoker.on_sync_invoke_ended_success = function(options, data) {
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.run_sync_invoker = function(options) {

    console.log("Options 1: " +  Object.entries(options));

    // Local variables
    let form_id = options["form_id"];
    let on_started_activate_blinking = options["on_started_activate_blinking"];
    let on_ended_draw_attention = options["on_ended_draw_attention"];

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
    if(form_id) {
        let form = $(form_id);
        let form_data = new FormData(form[0]);

        $.ajax({
            type: "POST",
            url: "address",// where you wanna post
            data: form_data,
            processData: false,
            contentType: false,
            error: function(jq_xhr, text_status, error_message) {
                let _on_error = function() {
                    $.fn.zato.invoker.on_sync_invoke_ended_error(options, jq_xhr, text_status, error_message);
                }
                setTimeout(_on_error, 290)
            },
            success: function(data) {
                let _on_success = function() {
                    $.fn.zato.invoker.on_sync_invoke_ended_on_success(options, data);
                }
                setTimeout(_on_success, 290)
            }
        });

    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
