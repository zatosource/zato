$.fn.zato.pubsub.message.details.on_validate_save = function(e) {

    var response = $.parseJSON(e.responseText);

    var expiration_time = response.expiration_time;
    if(!expiration_time) {
        expiration_time = '<span class="form_hint">---</span>';
    };

    $('#expiration_time').html(expiration_time);
    $('#size').html(response.size);
    $.fn.zato.user_message(response.is_ok, response.message);
}

$.fn.zato.pubsub.message.details.validate_save = function(e) {

    var form = $('#message-details-form');

    var is_valid_native = true; //form.get(0).reportValidity();
    var is_valid_chosen = $.fn.zato.is_form_valid(form);

    if(!is_valid_native || !is_valid_chosen) {
        return false
    }

    var data = form.serialize();
    $.fn.zato.post(
        String.format('/zato/pubsub/message/update/cluster/{0}/msg/{1}', $('#cluster_id').val(), $('#msg_id').val()),
        $.fn.zato.pubsub.message.details.on_validate_save, data);
    e.preventDefault();
}

$(document).ready(function() {
    var form = $('#message-details-form');
    $.fn.zato.data_table.set_field_required("#id_priority");
    $.fn.zato.data_table.set_field_required("#id_expiration");
    form.submit($.fn.zato.pubsub.message.details.validate_save);
})
