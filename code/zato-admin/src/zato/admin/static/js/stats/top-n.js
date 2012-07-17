$.fn.zato.stats.top_n.show_hide = function(selectors, show) {
    $.each(selectors, function(idx, selector) {
        var result = $(selector);
        if(show) {
            result.removeClass('hidden').addClass('visible');
        }
        else {
            result.removeClass('visible').addClass('hidden');
        }
    })
};

$.fn.zato.stats.top_n.switch_highlight = function(this_, remove_class, add_class) { 
    var id = $(this_).attr('id');
    id = _.last(_.str.words(id, '-'));
    if(id) {
      $('tr[id*="' +id+'"] > td').removeClass(remove_class).addClass(add_class);
    };
};

$.fn.zato.stats.top_n.data_callback = function(data, status) {

    var side = this['side'];

    var json = $.parseJSON(data.responseText);
    $(String.format('.{0}-loading-tr', side)).hide();
    
    var n_types = ['mean', 'usage'];
    $.each(n_types, function(idx, n_type) {
        $(String.format('#{0}-{1}-tr', side, n_type)).after(json[n_type]);
        $(String.format('#{0}-{1}', side, n_type)).tablesorter();
    });
    
    var show_hide = [String.format('.{0}-csv', side), '#compare_to'];

    if(json.has_stats) {

        var sparklines_options = {'width':'36px', 'height':'15px', 'lineColor':'#555', 'spotColor':false, 'fillColor':false}    

        $.fn.zato.stats.top_n.show_hide(show_hide, true);
        
        $(String.format('.{0}-trend', side)).sparkline('html', sparklines_options);
        $(String.format('#{0}-usage-csv', side)).attr('href', json.usage_csv_href);
        $(String.format('#{0}-mean-csv', side)).attr('href', json.mean_csv_href);
        
        $('.stats-table tr').mouseover(function() {
            $.fn.zato.stats.top_n.switch_highlight(this, 'default', 'hover');
        });
                
        $('.stats-table tr').mouseout(function(){
            $.fn.zato.stats.top_n.switch_highlight(this, 'hover', 'default');
       });
        
    }
    else {
        $.fn.zato.stats.top_n.show_hide(show_hide, false);
    }
};

$.fn.zato.stats.top_n.compare_to = function() {
    var compare_to_label = $(this).find(':selected').val();
    
    if(compare_to_label) {
    
        $.fn.zato.stats.top_n.show_hide(['#right-side'], true);
        $('.right-loading-tr').show();
        $('tr[id^="right-tr-mean"], tr[id^="right-tr-usage"]').empty().remove();
        
        var data = {};
        var keys = ['left_start', 'left_stop', 'n', 'cluster_id', 'id_compare_to'];
        
        $.each(keys, function(idx, key) {
            data[key] = $('#'+key).val();
        });
    };
    
    $.fn.zato.post('../data/', $.fn.zato.stats.top_n.data_callback, data, 'json', true, {'side': 'right'});
};

$(document).ready(function() {

    var data = {};
    var keys = ['cluster_id', 'left_start', 'left_stop', 'n'];
    var value = null;
    
    $.each(keys, function(idx, key) {
        value = $('#'+key).val();
        data[key.replace('left_', '')] = value;
    });
    
    $.fn.zato.post('../data/', $.fn.zato.stats.top_n.data_callback, data, 'json', true, {'side': 'left'});
    
    $('#id_compare_to').change($.fn.zato.stats.top_n.compare_to);
        
})
