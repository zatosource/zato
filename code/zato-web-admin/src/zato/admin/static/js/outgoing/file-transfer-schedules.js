// File transfer schedules - the per-connection list page. Each row is one
// recurring pickup task and the wizard page creates and edits them.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();

    // A row pointed to from the wizard's redirect wears the just-updated look
    var highlight = $(document).getUrlParam('highlight');
    if(highlight) {
        $('#tr_' + highlight).addClass('updated');
    }
});

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.file_transfer.schedules.delete_ = function(id, name) {

    var question = String.format('Are you sure you want to delete schedule `{0}`?', name);

    jConfirm(question, 'Please confirm', function(isConfirmed) {

        if(!isConfirmed) {
            return;
        }

        // Where the delete endpoint lives and which connection the schedule belongs to
        var deleteUrl = $('#ft-schedules-delete-url').val();
        var connId = $('#ft-schedules-conn-id').val();

        var callback = function(data, status) {

            if(status === 'success') {
                var row = document.getElementById('tr_' + id);
                $(row).animate({opacity: 0}, 200, function() {
                    $(row).remove();
                });

                var message = String.format('Schedule `{0}` deleted', name);
                $.fn.zato.user_message(true, message);
            }
            else {
                $.fn.zato.user_message(false, data.responseText);
            }
        };

        $.fn.zato.post(deleteUrl, callback, {'conn_id': connId, 'id': id}, 'text');
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
