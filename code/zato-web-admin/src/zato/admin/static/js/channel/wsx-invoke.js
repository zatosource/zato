$(document).ready(function() {

    _.each(['request_data', 'timeout'], function(name) {
        $.fn.zato.data_table.set_field_required('#' + name);
    });

    $('#send_message_form').bValidator();

    var _callback = function(data, status, xhr){
        var success = status == 'success';
        var response = success ? data.msg.response : data.responseText;
        $.fn.zato.user_message(success, response);
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
