$(document).ready(function() {

    _.each(['request_data', 'timeout'], function(name) {
        $.fn.zato.data_table.set_field_required('#' + name);
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

    $('#send_message_form').submit(function() {
        $(this).ajaxSubmit(options);
        return false;
    });
});
