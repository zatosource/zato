
$.fn.zato.pattern.delivery._update = function(action) {

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
	if(action != "delete") {
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

$.fn.zato.pattern.delivery.resubmit = function() {
	$.fn.zato.pattern.delivery._update("resubmit");
}

$.fn.zato.pattern.delivery.edit = function() {
	$.fn.zato.pattern.delivery._update("edit");
}

$.fn.zato.pattern.delivery.delete_ = function() {
    var callback = function(ok) {
        if(ok) {
		    $.fn.zato.pattern.delivery._update("delete");
		}
	};
	jConfirm('Are you sure you want to delete the task?', 'Please confirm', callback);	
}

$(document).ready(function() { 
    $("#resubmit1").click($.fn.zato.pattern.delivery.resubmit);
	$("#resubmit2").click($.fn.zato.pattern.delivery.resubmit);
	
    $("#delete1").click($.fn.zato.pattern.delivery.delete_);
	$("#delete2").click($.fn.zato.pattern.delivery.delete_);
	
    $("#update1").click($.fn.zato.pattern.delivery.edit);
	$("#update2").click($.fn.zato.pattern.delivery.edit);
	
	$("#look-up-task").click($.fn.zato.pattern.look_up_task);
	$("#look-up-form").submit($.fn.zato.pattern.look_up_task);
})
