$(document).ready(function() { 

    var _callback = function(data, status, xhr){
        var success = status == 'success';
        var msg = success ? data : data.responseText;
        $.fn.zato.user_message(success, msg);
    }    
        
    var options = { 
        success: _callback,
        error:  _callback,
        resetForm: false,
    }; 
        
    $('#request_response_configure_form').submit(function() { 
        $(this).ajaxSubmit(options); 
        return false; 
    });

}); 
