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

    var prefixes = ['left-tr-mean-', 'left-tr-usage-', 'right-tr-mean-', 'right-tr-usage-'];
    $.each(prefixes, function(idx, prefix) {
        id = id.replace(prefix, '');
    });

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

    var directions = ['utc_start', 'utc_stop', 'user_start', 'user_stop'];

    $.each(directions, function(idx, time) {
        if(json[time]) {
            $(String.format('#{0}-{1}', side, time)).val(json[time]);
            if($.fn.zato.startswith(time, 'user')) {
                $(String.format('#{0}-{1}-label', side, time)).text(json[time+'_label']);
            }
        }
        if(directions[idx] == 'user_stop' && !json[time]) {
            $('.direction-optional').addClass('hidden');
        }
    });

    if(json.is_custom || json.is_trends) {
        $.fn.zato.toggle_visible_hidden('#right-user_stop-hyphen', true);
        $.fn.zato.toggle_visible_hidden('#right-user_stop-label', true);
    }
    else {
        $.fn.zato.toggle_visible_hidden('#right-user_stop-hyphen', false);
        $.fn.zato.toggle_visible_hidden('#right-user_stop-label', false);
    }

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

$.fn.zato.stats.top_n.shift = function(side, shift, date_prefix) {
    var data = {};

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

    var keys = [
        String.format('{0}-utc_start', date_prefix),
        String.format('{0}-utc_stop', date_prefix),
        String.format('{0}-user_start', date_prefix),
        String.format('{0}-user_stop', date_prefix),
        'n',
        'cluster_id',
    ];

    if(date_prefix == 'custom') {
        keys.push('custom_range');
    }

    $.each(keys, function(idx, key) {
        data[key.replace('left-', '').replace('right-', '').replace('custom-', '')] = $('#'+key).val();
    });

    data['side'] = side;
    data['shift'] = shift;
    data['choice'] = $('#choice').val();

    $.fn.zato.post('../data/', $.fn.zato.stats.top_n.data_callback, data, 'json', true, {'side': side});
}

$.fn.zato.stats.top_n.show_start_stop_picker = function() {
    var div = $('#custom_date');
    div.prev().text('Choose start/end dates for the right-side statistics'); // prev() is a .ui-dialog-titlebar
    div.dialog('open');
}

$.fn.zato.stats.top_n.change_date = function(side, shift) {
    $('#shift').val('');
    if(side == 'left') {
        $('#page_label').text('Custom set, step one ' + $('#step').val());
    }

    $.fn.zato.stats.top_n.shift(side, shift);
};

$.fn.zato.stats.top_n.initial_data = function() {
    if($('#cluster_id').val()) {
        var data = {};
        var keys = ['cluster_id', 'left-utc_start', 'left-utc_stop', 'left-user_start', 'left-user_stop', 'n'];
        var value = null;

        $.each(keys, function(idx, key) {
            value = $('#'+key).val();
            data[key.replace('left-', '')] = value;
        });

        data['side'] = 'left';
        data['choice'] = $('#choice').val();

        $.fn.zato.post('../data/', $.fn.zato.stats.top_n.data_callback, data, 'json', true, {'side': 'left'});
    }
};

$.fn.zato.stats.top_n.on_custom_date = function() {
    var custom_date_form_id = '#form-custom_date'
    var custom_date_form = $(custom_date_form_id);

    if(custom_date_form.data('QQQ-zvalidator').isValid()) {
        $.fn.zato.stats.top_n.shift('right', '', 'custom');
        $.fn.zato.data_table.cleanup(custom_date_form_id);
        return true;
    }
};

$.fn.zato.stats.top_n.setup_forms = function() {

    $.each(['start', 'stop'], function(ignored, suffix) {
        var field_id = String.format('#custom-user_{0}', suffix)
        $(field_id).attr('data-QQQ-zvalidator', 'required');
        $(field_id).attr('data-QQQ-zvalidator-msg', 'This is a required field');

        $(field_id).datetimepicker(
            {
                'dateFormat':$('#js_date_format').val(),
                'timeFormat':$('#js_time_format').val(),
                'ampm':$.fn.zato.to_bool($('#js_ampm').val()),
            }
        );

    });

    var custom_date_form_id = '#form-custom_date'
    var custom_date_form = $(custom_date_form_id);

    custom_date_form.submit(function(e) {
        e.preventDefault();
        if($.fn.zato.stats.top_n.on_custom_date()) {
            $('#custom_date').dialog('close');
        }
    });

    custom_date_form.QQQ-zvalidator();

    $('#custom_date').dialog({
        autoOpen: false,
        width: '40em',
        close: function(e, ui) {
            $.fn.zato.data_table.reset_form(custom_date_form_id);
        }
    });
}

$(document).ready(function() {
    $.fn.zato.stats.top_n.setup_forms();
    $.fn.zato.stats.top_n.initial_data();
})
