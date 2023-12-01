
$(document).ready(function() {

    var fields = ['scheduler_raw_times_interval', 'scheduler_raw_times_batch',
        'scheduler_per_minute_aggr_interval', 'atttention_slow_threshold', 'atttention_top_threshold']

    $.each(fields, function(ignored, suffix) {
        var id = '#id_' + suffix;
        $(id).attr('data-QQQ-zvalidator', 'digit,required');
        $(id).attr('data-QQQ-zvalidator-msg', 'Enter an integer');
    })

    $('#settings_form').QQQ-zvalidator();
});
