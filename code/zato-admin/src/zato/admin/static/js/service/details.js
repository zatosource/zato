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
        
    $('#invoke_service_form').submit(function() { 
        $(this).ajaxSubmit(options); 
        return false; 
    });
    
    var sparklines_options = {'width':'120px', 'height':'15px', 'lineColor':'#555', 'spotColor':false, 'disableHiddenCheck':true,
                               'fillColor':false}
    
   $('#trend_mean_1h').sparkline('html', sparklines_options);
   $('#trend_rate_1h').sparkline('html', sparklines_options); 

}); 
