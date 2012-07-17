$(document).ready(function() {

    var sparklines_options = {'width':'46px', 'height':'15px', 'lineColor':'#555', 'spotColor':false, 'fillColor':false}

    var _callback = function(data, status) {
        var json = $.parseJSON(data.responseText);
        $('.loading-tr').remove();
        
        var n_types = ['mean', 'usage'];
        $.each(n_types, function(idx, n_type) {
            $(String.format('#left-{0}-tr', n_type)).after(json[n_type]);
            $(String.format('#left-{0}', n_type)).tablesorter();
        });

        if(json.has_stats) {
            $('.left-csv').removeClass('hidden').addClass('visible');
            $('.trend').sparkline('html', sparklines_options);
            $('#left-usage-csv').attr('href', json.usage_csv_href);
            $('#left-mean-csv').attr('href', json.mean_csv_href);
            
            var _switch_highlight = function(this_, remove_class, add_class) { 
                var id = $(this_).attr('id');
                id = _.last(_.str.words(id, '-'));
                if(id) {
                  $('tr[id*="' +id+'"] > td').removeClass(remove_class).addClass(add_class);
                };
            };
            
            $('.stats-table tr').mouseover(function() {
                _switch_highlight(this, 'default', 'hover');
            });
                    
            $('.stats-table tr').mouseout(function(){
                _switch_highlight(this, 'hover', 'default');
           });
            
        }
        else {
            $('.left-csv').removeClass('visible').addClass('hidden');
        }
        
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
