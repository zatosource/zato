
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.as2_keystore.config = {
    success_message: 'Keystore saved',
    error_message: 'Keystore could not be saved',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.as2_keystore.show_message = function(is_success, message) {
    var css_class = is_success ? 'user-message-success' : 'user-message-failure';
    $('#user-message').removeClass('user-message-success user-message-failure').addClass(css_class).text(message);
    $('#user-message-div').show();
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.as2_keystore.on_save_complete = function(xhr) {
    var data = JSON.parse(xhr.responseText);
    if(data.is_ok) {
        $.fn.zato.as2_keystore.show_message(true, data.message);
    }
    else {
        $.fn.zato.as2_keystore.show_message(false, data.message);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {

    $('#keystore-form').submit(function(e) {
        e.preventDefault();

        var form = $(this);
        $.fn.zato.post(form.attr('action'), $.fn.zato.as2_keystore.on_save_complete, form.serialize(), 'text');
    });

})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
