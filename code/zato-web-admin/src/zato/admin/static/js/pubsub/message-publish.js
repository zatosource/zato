$.fn.zato.pubsub.message.publish.on_validate_save = function(e) {

    var response = $.parseJSON(e.responseText);
    $.fn.zato.user_message(response.is_ok, response.message);
}

$.fn.zato.pubsub.message.publish.validate_save = function(e) {

    var form = $('#message-publish-form');

    var is_valid_native = true; //form.get(0).reportValidity();
    var is_valid_chosen = $.fn.zato.is_form_valid(form);

    if(!is_valid_native || !is_valid_chosen) {
        return false
    }

    var data = form.serialize();
    $.fn.zato.post('/zato/pubsub/message/publish-action/',
        $.fn.zato.pubsub.message.publish.on_validate_save, data);

    e.preventDefault();
}

$(document).ready(function() {
    var form = $('#message-publish-form');
    $.fn.zato.data_table.set_field_required("#id_priority");
    $.fn.zato.data_table.set_field_required("#id_expiration");
    form.submit($.fn.zato.pubsub.message.publish.validate_save);
})
