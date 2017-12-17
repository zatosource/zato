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
    var data = form.serialize();
    $.fn.zato.post(
        String.format('/zato/pubsub/message/update/cluster/{0}/msg/{1}', $('#cluster_id').val(), $('#msg_id').val()),
        $.fn.zato.pubsub.message.details.on_validate_save, data);
    e.preventDefault();
}

$.fn.zato.pubsub.message.details.toggle_time = function(link_name, current_value, new_value) {
    var elem = $('#a_' + link_name);
    var href_format = "javascript:$.fn.zato.pubsub.message.details.toggle_time('{0}', '{1}', '{2}')"
    var href_value = String.format(href_format, link_name, new_value, current_value);

    elem.attr('href', href_value);
    elem.html(new_value);

}


$(document).ready(function() {

    $('#id_priority').attr('data-bvalidator', 'digit,between[1:9],required');
    $('#id_priority').attr('data-bvalidator-msg', 'Must be a valid priority');

    $('#id_expiration').attr('data-bvalidator', 'digit');
    $('#id_expiration').attr('data-bvalidator-msg', 'Must be an integer');

    $('#id_mime_type').attr('data-bvalidator', 'required');
    $('#id_mime_type').attr('data-bvalidator-msg', 'This is a required field');

    $('#data-textarea').attr('data-bvalidator', 'required');
    $('#data-textarea').attr('data-bvalidator-msg', 'This is a required field');

    var form = $('#message-details-form');

    form.bValidator()
    form.submit($.fn.zato.pubsub.message.details.validate_save);
})
