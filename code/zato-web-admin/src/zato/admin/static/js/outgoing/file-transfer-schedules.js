// File transfer schedules - the per-connection list page. Each row is one
// recurring pickup task and the wizard page creates new ones.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
});

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.file_transfer.schedules.delete_ = function(name) {

    // UI preview - removes the row on screen only, the real delete
    // arrives together with the backend services.
    var question = String.format('Are you sure you want to delete schedule `{0}`?', name);

    jConfirm(question, 'Please confirm', function(isConfirmed) {

        if(!isConfirmed) {
            return;
        }

        var row = document.getElementById('tr_' + name);
        $(row).animate({opacity: 0}, 200, function() {
            $(row).remove();
        });

        var message = String.format('Schedule `{0}` deleted', name);
        $.fn.zato.user_message(true, message);
    });
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
