$(document).ready(function() {

    // Local variables
    var form = $('#cache_entry_form');

    // Make certain elements required
    _.each(['key', 'key_data_type', 'value_data_type', 'expiry'], function(name) {
        $.fn.zato.data_table.set_field_required('#id_' + name);
    });

    var _callback = function(data, status, xhr) {
        var success = status == 'success';
        var msg = success ? data.msg : data.responseText;
        $.fn.zato.user_message(success, msg);

        var action = $('#action').val();
        var key_value = $('#id_key').val();
        var old_key = $('#id_old_key');

        if(success) {
            old_key.val(key_value);
            window.history.pushState({} , '', data.new_path);
        }
    }

    var options = {
        success: _callback,
        error:  _callback,
        resetForm: false,
        'dataType': 'json',
    };

    form.submit(function() {

        // Do not proceed unless the form is valid
        if(!$.fn.zato.is_form_valid(form)) {
            return false;
        }

        $(this).ajaxSubmit(options);
        return false;
    });
});
