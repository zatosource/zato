
//
// A simple function for returning a random string.
//
function get_random_string() {
    var elems = '1234567890qwertyuiopasdfghjklzxcvbnm'.split('');
    var s = "";
    var length = 32;

    for(var i = 0; i < length; i++) {
        s += elems[Math.floor(Math.random() * elems.length)];
    }
    return s;
}

//
// A utility function for providing a feedback to the user.
//
function update_user_message(is_success, response, user_message_elem,
                                user_message_container_elem) {

    if(!user_message_elem)
        user_message_elem = "user-message";

    if(!user_message_container_elem)
        user_message_container_elem = "user-message-div";

    var css_class_name = "user-message ";

    if(is_success) {
        css_class_name += "user-message-success"
    }
    else {
        css_class_name += "user-message-failure"
    };

    $(user_message_elem).className = css_class_name;
    $(user_message_elem).innerHTML = new String(response).escapeHTML();
    Effect.Fade(user_message_container_elem, {duration: 0.4, from:1.0, to:0.1, queue:"start"}),
    Effect.Appear(user_message_container_elem, {duration: 0.4, queue:"end"});
}

function to_bool(item) {
    return new String(item).toLowerCase() == "true";
}