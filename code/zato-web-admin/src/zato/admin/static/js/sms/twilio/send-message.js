$(document).ready(function() {

    _.each(['body', 'from_', 'to'], function(name) {
        $.fn.zato.data_table.set_field_required('#' + name);
    });

    var _callback = function(data, status, xhr){
        var success = status == 'success';
        var msg = success ? data.msg : data.responseText;
        $.fn.zato.user_message(success, msg);
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
