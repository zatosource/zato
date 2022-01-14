$(document).ready(function() { 

   var sparklines_options = {'width':'120px', 'height':'15px', 'lineColor':'#555', 'spotColor':false, 'disableHiddenCheck':true,
                               'fillColor':false}
    
   $('#trend_mean_1h').sparkline('html', sparklines_options);
   $('#trend_rate_1h').sparkline('html', sparklines_options); 

}); 
