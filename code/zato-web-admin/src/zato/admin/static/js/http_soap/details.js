
/*
# ##############################################################################
*/

$.fn.zato.http_soap.details.submit = function(e, form_id, callback) {
    var form = $(form_id);
    var data = form.serialize();
    $.fn.zato.post(form.attr('action'), callback, data);
    e.preventDefault();
}

/*
# ##############################################################################
*/

$.fn.zato.http_soap.details.on_audit_set_state_callback = function(e) {
    var is_ok = e.statusText == 'OK';
    $.fn.zato.user_message(is_ok, e.responseText);
    if(is_ok) {
        var span = $('#audit-set-state-span');
        var button = $('#audit-set-state-button');
        var hidden = $('#audit_enabled');

        if(hidden.val() == 'False') {
            span.text('Enabled ');
            hidden.val('True');
            button.text('Click to disable');
        }
        else {
            span.text('Disabled');
            hidden.val('False');
            button.text('Click to enable');
        }
    }
}

$.fn.zato.http_soap.details.audit_set_patterns_callback = function(e) {
    $.fn.zato.user_message(e.statusText == 'OK', e.responseText);
}

/*
# ##############################################################################
*/

$.fn.zato.http_soap.details.audit_set_state = function(e) {
    $.fn.zato.http_soap.details.submit(e, '#audit-set-state',
        $.fn.zato.http_soap.details.on_audit_set_state_callback);
}

$.fn.zato.http_soap.details.audit_set_patterns = function(e) {
    $.fn.zato.http_soap.details.submit(e, '#audit-set-config',
        $.fn.zato.http_soap.details.audit_set_patterns_callback);
}

/*
# ##############################################################################
*/

$(document).ready(function() {

    $.fn.zato.data_table.set_field_required('#id_msg_pattern_type_id');
    $.fn.zato.data_table.set_field_required('#id_audit_max_payload');

    $("#audit-set-config").bValidator();

    $("#audit-set-state").submit($.fn.zato.http_soap.details.audit_set_state);
    $("#audit-set-config").submit($.fn.zato.http_soap.details.audit_set_patterns);
})
