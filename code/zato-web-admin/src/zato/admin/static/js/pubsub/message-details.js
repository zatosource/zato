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

$.fn.zato.pubsub.message.details.toggle_time = function(link_name) {
    var elem = $('#a_' + link_name);
    var current_value = elem.text();

    var callback = function(data, status) {
        elem.html(data.responseText);
    }

    var url = String.format(
        '/zato/pubsub/message/toggle-time/cluster/{0}/value/{1}/', $('#cluster_id').val(), current_value);

    $.fn.zato.post(url, callback, '', 'text', true);

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
