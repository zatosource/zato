
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

(function() {
    YAHOO.namespace('widget.alert');

    alert_old = window.alert;
    window.alert = function(str) {
        YAHOO.widget.alert.dlg.setBody(str);
        YAHOO.widget.alert.dlg.cfg.queueProperty('icon', YAHOO.widget.SimpleDialog.ICON_WARN);
        YAHOO.widget.alert.dlg.cfg.queueProperty('zIndex', 9999);
        YAHOO.widget.alert.dlg.render(document.body);
        if (YAHOO.widget.alert.dlg.bringToTop) {
            YAHOO.widget.alert.dlg.bringToTop();
        }
        YAHOO.widget.alert.dlg.show();
    };


    YAHOO.util.Event.on(window, 'load', function() {

        var handleOK = function() {
            this.hide();
        };

        YAHOO.widget.alert.dlg = new YAHOO.widget.SimpleDialog('widget_alert', {
            visible:false,
            width: '20em',
            zIndex: 9999,
            close: false,
            fixedcenter: true,
            modal: false,
            draggable: true,
            constraintoviewport: true, 
            icon: YAHOO.widget.SimpleDialog.ICON_WARN,
            buttons: [
                { text: 'OK', handler: handleOK, isDefault: true }
                ]
        });
        YAHOO.widget.alert.dlg.setHeader("");
        YAHOO.widget.alert.dlg.setBody('Alert body passed to window.alert'); // Bug in panel, must have a body when rendered
        YAHOO.widget.alert.dlg.render(document.body);
    });
})();

function to_bool(item) {
    return new String(item).toLowerCase() == "true";
}