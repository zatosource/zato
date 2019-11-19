$.fn.zato.pubsub.message.publish.on_validate_save = function(e) {

    var response = $.parseJSON(e.responseText);
    $.fn.zato.user_message(response.is_ok, response.message);
}

$.fn.zato.pubsub.message.publish.validate_save = function(e) {

    var form = $('#message-publish-form');
    var data = form.serialize();
    $.fn.zato.post('/zato/pubsub/message/publish-action/',
        $.fn.zato.pubsub.message.publish.on_validate_save, data);

    e.preventDefault();
}

$(document).ready(function() {

    $('#id_topic_name').attr('data-bvalidator', 'required');
    $('#id_topic_name').attr('data-bvalidator-msg', 'This is a required field');

    $('#id_publisher_id').attr('data-bvalidator', 'required');
    $('#id_publisher_id').attr('data-bvalidator-msg', 'This is a required field');

    $('#data-textarea').attr('data-bvalidator', 'required');
    $('#data-textarea').attr('data-bvalidator-msg', 'This is a required field');

    $('#id_priority').attr('data-bvalidator', 'digit,between[1:9],required');
    $('#id_priority').attr('data-bvalidator-msg', 'Must be a valid priority');

    $('#id_expiration').attr('data-bvalidator', 'digit');
    $('#id_expiration').attr('data-bvalidator-msg', 'Must be an integer');

    $('#data-textarea').attr('data-bvalidator', 'required');
    $('#data-textarea').attr('data-bvalidator-msg', 'This is a required field');

    var form = $('#message-publish-form');

    form.bValidator()
    form.submit($.fn.zato.pubsub.message.publish.validate_save);
})
