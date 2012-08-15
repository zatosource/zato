
$(document).ready(function() { 

    $.each(['start', 'stop'], function(ignored, suffix) {
        var id = 'id_' + suffix;
        var jq_id = '#' + id;
        
        $(jq_id).attr('data-bvalidator', 'required');
        $(jq_id).attr('data-bvalidator-msg', 'This is a required field');
        
    
	    // Picker
	    $(jq_id).datetimepicker();

    })
    
    $('#maintenance_form').bValidator();

});

