$.fn.zato.pattern.look_up_task = function(e) {
    if(e) {
		e.preventDefault();
	}
	window.location.href = String.format('/zato/pattern/delivery/details/{0}/?cluster={1}', $("#look-up-task-name").val(), $("#cluster_id").val());
}