$(document).ready(function() {

    var sparklines_options = {'width':'110px', 'height':'15px', 'lineColor':'#555', 'spotColor':false, 'disableHiddenCheck':true, 'fillColor':false}
    $('.trend').sparkline('html', sparklines_options);
    
    $('.stats-table').tablesorter();

})