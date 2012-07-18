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
    
    var show_hide = [String.format('.{0}-csv', side), '#compare_to', String.format('.{0}-date', side)];
    
    $.each(['start', 'stop'], function(idx, time) {
        $(String.format('#{0}-{1}', side, time)).val(json[time]);
        $(String.format('#{0}-{1}-label', side, time)).text(json[time]);
    });
    
    $.fn.zato.stats.top_n.show_hide([String.format('.{0}-date', side)], true);
    
    /* The right side has never been shown yet so we need to update its start/stop
       parameters even though the shift was on the left one.
    */

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
};

$.fn.zato.stats.top_n._shift = function(side, shift, date_prefix) {
    var data = {};
    
    if(shift) {
        if(side == 'right') {
            $.fn.zato.stats.top_n.show_hide(['#right-side'], true);
        }
        
        if(!date_prefix) {
            date_prefix = side;
        }
        
        $.each(['csv', 'date'], function(idx, elem) {
            $.fn.zato.stats.top_n.show_hide([String.format('{0}-{1}', side, elem)], false);
        });

        $(String.format('.{0}-loading-tr', side)).show();
        $(String.format('tr[id^="{0}-tr-mean"], tr[id^="{0}-tr-usage"]', side)).empty().remove();
        
        var keys = [String.format('{0}-start', date_prefix), String.format('{0}-stop', date_prefix), 'n', 'cluster_id'];
        
        $.each(keys, function(idx, key) {
            data[key.replace('left-', '').replace('right-', '')] = $('#'+key).val();
        });
        
        data['side'] = side;
        data['shift'] = shift;
    }
    
    $.fn.zato.post('../data/', $.fn.zato.stats.top_n.data_callback, data, 'json', true, {'side': side});
}

$.fn.zato.stats.top_n.compare_to = function() {
    var shift = $(this).find(':selected').val();
    $.fn.zato.stats.top_n._shift('right', shift, 'left');
};

$.fn.zato.stats.top_n.change_date = function(side, shift) {
    if(side == 'right') {
        $('#shift').val('');
    }
    else {
        $('#page_label').text('Custom set by hour')
    }
    $.fn.zato.stats.top_n._shift(side, shift);
};

$(document).ready(function() {

    var data = {};
    var keys = ['cluster_id', 'left-start', 'left-stop', 'n'];
    var value = null;
    
    $.each(keys, function(idx, key) {
        value = $('#'+key).val();
        data[key.replace('left-', '')] = value;
    });
    
    data['side'] = 'left';
    $.fn.zato.post('../data/', $.fn.zato.stats.top_n.data_callback, data, 'json', true, {'side': 'left'});
    $('#shift').change($.fn.zato.stats.top_n.compare_to);
        
})
