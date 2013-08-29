
$.fn.zato.pattern.delivery.in_doubt._update = function(action) {

    var _callback = function(data, status) {
        var success = status == "success";
        var msg;
		if(success) {
		    msg = $.parseJSON(data.responseText)["message"];
		}
		else {
			msg = data.responseText;
		}
        $.fn.zato.user_message(success, msg);
    }
	
	var data = {};
	if(action == "resubmit") {
		data["payload"] = $("#payload").val();
		data["args"] = $("#args").val();
		data["kwargs"] = $("#kwargs").val();
	}
	
    $.ajax({
        type: "POST",
        url: String.format("/zato/pattern/delivery/{0}/{1}/{2}/", action, $("#task_id").val(), $("#cluster_id").val()),
        data: data,
		dataType: "json",
        headers: {"X-CSRFToken": $.cookie("csrftoken")},
        complete: _callback
    });
}

$.fn.zato.pattern.delivery.in_doubt.resubmit = function() {
	$.fn.zato.pattern.delivery.in_doubt._update("resubmit");
}

$.fn.zato.pattern.delivery.in_doubt.delete_ = function() {
	$.fn.zato.pattern.delivery.in_doubt._update("delete");
}

$(document).ready(function() { 
    $("#resubmit1").click($.fn.zato.pattern.delivery.in_doubt.resubmit);
	$("#resubmit2").click($.fn.zato.pattern.delivery.in_doubt.resubmit);
	
    $("#delete1").click($.fn.zato.pattern.delivery.in_doubt.delete_);
	$("#delete2").click($.fn.zato.pattern.delivery.in_doubt.delete_);
})
