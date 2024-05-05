
$(document).ready(function() {
    $('#invoke-service').click($.fn.zato.invoker.on_invoke_submitted);
});

$.fn.zato.invoker.on_invoke_submitted = function() {

    const options = {
        "on_started_activate_blinking": ["#invoking-please-wait"],
        "on_ended": 123,
    }
    $.fn.zato.invoker.run_sync_invoker(options);
}

$.fn.zato.invoker.run_sync_invoker = function(options) {

    console.log("Options 1: " +  Object.entries(options));
    console.log("Options 2: " + options["on_started_activate_blinking"]);

    let on_started_activate_blinking = options["on_started_activate_blinking"];

    // Start by enabling blinking for all the elements that should blink
    on_started_activate_blinking.each(function(elem) {
        $.fn.zato.toggle_css_class($(elem), "hidden", "invoker-blinking");
    });

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

}

$.fn.zato.invoker.invoke = function() {
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
