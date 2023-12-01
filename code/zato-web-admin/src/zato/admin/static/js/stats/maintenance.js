
$(document).ready(function() {

    $.each(['start', 'stop'], function(ignored, suffix) {
        var id = 'id_' + suffix;
        var jq_id = '#' + id;

        $(jq_id).attr('data-QQQ-zvalidator', 'required');
        $(jq_id).attr('data-QQQ-zvalidator-msg', 'This is a required field');

        $(jq_id).datetimepicker(
            {
                'dateFormat':$('#js_date_format').val(),
                'timeFormat':$('#js_time_format').val(),
                'ampm':$.fn.zato.to_bool($('#js_ampm').val()),
            }
        );

    })

    $('#maintenance_form').QQQ-zvalidator();

});
