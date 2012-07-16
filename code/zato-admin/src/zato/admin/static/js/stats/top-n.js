$(document).ready(function() {

    var sparklines_options = {'width':'80px', 'height':'15px', 'lineColor':'#555', 'spotColor':false, 'fillColor':false}

    var _callback = function(data, status) {
        var json = $.parseJSON(data.responseText);
        $('.loading-tr').remove();
        
        var n_types = ['mean', 'usage'];
        $.each(n_types, function(idx, n_type) {
            $(String.format('#left-{0}-tr', n_type)).after(json[n_type]);
            $(String.format('#left-{0}', n_type)).tablesorter();
        });
        
        $('.trend').sparkline('html', sparklines_options);    

    };
    
    var data = {};
    var keys = ['cluster_id', 'left_start', 'left_stop', 'n'];
    var value = null;
    
    $.each(keys, function(idx, key) {
        value = $('#'+key).val();
        data[key.replace('left_', '')] = value;
    });
    
    $.fn.zato.post('../data/', _callback, data, 'json', true);
        
})