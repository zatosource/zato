
$(document).ready(function() { 

    $.each(['from', 'to'], function(ignored, suffix) {
        var id = 'id_delete_' + suffix;
        var jq_id = '#' + id;
        
        $(jq_id).attr('data-bvalidator', 'required');
        $(jq_id).attr('data-bvalidator-msg', 'This is a required field');
        
    
	    // Picker
	    AnyTime.picker(id,
		    {format: '%Y-%m-%d %T', 
		    firstDOW: 1, // Weeks start on Monday
		    });
        
    })
    
    $('#maintenance_form').bValidator();

});
