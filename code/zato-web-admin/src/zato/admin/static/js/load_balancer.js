
$.fn.zato.load_balancer.on_validate_save = function(e) {
    $.fn.zato.user_message(e.statusText == 'OK', e.responseText);
}

$.fn.zato.load_balancer._validate_save = function(e, extra) {
    var form = $("#lb-validate-save");
    var data = form.serialize();
    data += String.format("&{0}=1", extra);
    $.fn.zato.post(form.attr('action'), $.fn.zato.load_balancer.on_validate_save, data);
    e.preventDefault();
}

$.fn.zato.load_balancer.validate = function(e) {
    $.fn.zato.load_balancer._validate_save(e, 'validate');
}

$.fn.zato.load_balancer.validate_save = function(e) {
    $.fn.zato.load_balancer._validate_save(e, 'validate_save');
}

$(document).ready(function() { 
    $("#validate").click($.fn.zato.load_balancer.validate);
    $("#validate_save").click($.fn.zato.load_balancer.validate_save);
})
