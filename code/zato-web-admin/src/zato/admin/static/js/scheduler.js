
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Job = new Class({
    toString: function() {
        var s = '<Job id:{0} name:{1} is_active:{2} job_type:{3} service:{4}>';
        return String.format(s, this.id, this.name, this.is_active, this.job_type,
            this.service);
    }
});

$(document).ready(function() { 

    $('#data-table').tablesorter(); 
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.Job;
    $.fn.zato.data_table.parse();
    
    var actions = ['create', 'edit'];
    var job_types = ['one_time', 'interval_based', 'cron_style'];

    /* Dynamically prepare pop-up windows and date-time pickers.
    */
    $.each(job_types, function(ignored, job_type) {
        $.each(actions, function(ignored, action) {
            var form_id = String.format('#{0}-form-{1}', action, job_type);
            var div_id = String.format('#{0}-{1}', action, job_type);
            var picker_id = String.format('id_{0}-{1}-start_date', action, job_type);

            // Pop-up                
            $(div_id).dialog({
                autoOpen: false,
                width: '40em',
                close: function(e, ui) {
                    $.fn.zato.data_table.reset_form(form_id);
                }
            });
            
            $('#'+picker_id).datetimepicker(
                {
                    'dateFormat':$('#js_date_format').val(),
                    'timeFormat':$('#js_time_format').val(),
                    'ampm':$.fn.zato.to_bool($('#js_ampm').val()),
                }
            );
        });
    });
    
    /* Prepare the validators here so that it's all still a valid HTML
       even with bValidator's custom attributes.
    */

    var one_time_attrs = ['name', 'start_date', 'service'];        
    var interval_based_attrs = ['name', 'start_date', 'service'];
    var cron_style_attrs = ['name', 'start_date', 'cron_definition', 'service'];

    var job_types_dict = {
        'one_time':one_time_attrs,
        'interval_based':interval_based_attrs,
        'cron_style':cron_style_attrs
    };
    
    var field_id = null;
    
    $.each(actions, function(ignored, action) {
        $.each(_.keys(job_types_dict), function(ignored, job_type) {
            var attrs = job_types_dict[job_type];
            $.each(attrs, function(ignored, attr) {
                field_id = String.format('#id_{0}-{1}-{2}', action, job_type, attr)
                $(field_id).attr('data-bvalidator', 'required');
                $(field_id).attr('data-bvalidator-msg', 'This is a required field');
            });
            var form_id = String.format('#{0}-form-{1}', action, job_type)
            $(form_id).bValidator();
        });
    });
    
    /* Assign form submition handlers.
    */
    
    $.each(job_types, function(ignored, job_type) {
        $.each(actions, function(ignored, action) {
            $('#'+ action +'-'+ job_type).submit(function() {
                $.fn.zato.scheduler.data_table.on_submit(action, job_type);
                return false;
            });
        });
    });
}); 

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.scheduler.titles = {
    'one_time': 'a one-time',
    'interval_based': 'an interval-based',
    'cron_style': 'a cron-style',
}

$.fn.zato.scheduler.data_table.on_submit_complete = function(data, status, 
    action, job_type) {

    if(status == 'success') {
        var json = $.parseJSON(data.responseText);
        var include_tr = true ? action == 'create' : false;
        var row = $.fn.zato.scheduler.data_table.add_row(json, action, job_type, include_tr);
        if(action == 'create') {
        
            if($('#data-table').data('is_empty')) {
                $('#data-table tr:last').remove();
            }
            
            $('#data-table').data('is_empty', false);
            $('#data-table > tbody:last').prepend(row);
        }
        else {
            var tr = $.fn.zato.data_table.row_updated(json.id);
            tr.html(row);
        }    
    }

    $.fn.zato.data_table._on_submit_complete(data, status);
    $.fn.zato.data_table.cleanup('#'+ action +'-form-'+ job_type);
}

$.fn.zato.scheduler.data_table.on_submit = function(action, job_type) {
    var form = $('#' + action +'-form-'+ job_type);
    var callback = function(data, status) {
            return $.fn.zato.scheduler.data_table.on_submit_complete(data, 
                status, action, job_type);
        }
    return $.fn.zato.data_table._on_submit(form, callback);
}

$.fn.zato.scheduler._create_edit = function(action, job_type, id) {

    var title = String.format('{0} {1} job', 
        action.capitalize(), $.fn.zato.scheduler.titles[job_type]);
        
    if(action == 'edit') {

        var form = $('#' + action +'-form-'+ job_type);
        var name_prefix = String.format('{0}-{1}-', action, job_type);
        var id_prefix = '#id_' + name_prefix
        var instance = $.fn.zato.data_table.data[id];

        $.fn.zato.form.populate(form, instance, name_prefix, id_prefix);

    }

    var div = $('#'+ action +'-'+ job_type);
    div.prev().text(title); // prev() is a .ui-dialog-titlebar
    div.dialog('open');
}

$.fn.zato.scheduler.data_table.new_row = function(job, data, include_tr) {
    var row = '';
    
    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", job.id);
    }
    
    var cluster_id = $(document).getUrlParam('cluster');
    
    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', job.name);
    row += String.format('<td>{0}</td>', job.is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', friendly_names[job.job_type]);
    row += String.format('<td>{0}</td>', data.definition_text);
    row += String.format('<td>{0}</td>', $.fn.zato.data_table.service_text(job.service, cluster_id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.scheduler.execute({0})'>Execute</a>", job.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.scheduler.edit('{0}', {1})\">Edit</a>", job.job_type, job.id));
    row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.scheduler.delete_({0});'>Delete</a>", job.id));
    row += String.format("<td class='ignore job_id_{0}'>{0}</td>", job.id);
    row += String.format("<td class='ignore'>{0}</td>", job.is_active);
    row += String.format("<td class='ignore'>{0}</td>", job.job_type);
    row += String.format("<td class='ignore'>{0}</td>", job.start_date);
    row += String.format("<td class='ignore'>{0}</td>", job.extra);

    weeks = job.weeks ? 'weeks' in job : '';
    days = job.days ? 'days' in job : '';
    hours = job.hours ? 'hours' in job : '';
    minutes = job.minutes ? 'minutes' in job : '';
    seconds = job.seconds ? 'seconds' in job : '';
    repeats = job.repeats ? 'repeats' in job : '';
    cron_definition = job.cron_definition ? 'cron_definition' in job : '';
    
    row += String.format("<td class='ignore'>{0}</td>", weeks);
    row += String.format("<td class='ignore'>{0}</td>", days);
    row += String.format("<td class='ignore'>{0}</td>", hours);
    row += String.format("<td class='ignore'>{0}</td>", minutes);
    row += String.format("<td class='ignore'>{0}</td>", seconds);
    row += String.format("<td class='ignore'>{0}</td>", repeats);
    row += String.format("<td class='ignore'>{0}</td>", cron_definition);
    
    if(include_tr) {
        row += '</tr>';
    }
    
    return row;
}

$.fn.zato.scheduler.data_table.add_row = function(data, action, job_type, include_tr) {

    var job = new $.fn.zato.data_table.Job();
    var form = $(String.format('#{0}-form-{1}', action, job_type));
    var prefix = String.format('{0}-{1}-', action, job_type);
    var name = null;
    
    $.each(form.serializeArray(), function(idx, elem) {
        if(elem.name.indexOf(prefix) === 0) {
            name = elem.name.replace(prefix, '');
            job[name] = elem.value;
        }
    })
    
    job.id = data.id;
    job.is_active = $.fn.zato.to_bool(job.is_active);
    job.job_type = job_type;
    
    $.fn.zato.data_table.data[job.id] = job;
    return $.fn.zato.scheduler.data_table.new_row(job, data, include_tr);
}

$.fn.zato.scheduler.create = function(job_type) {
    $.fn.zato.scheduler._create_edit('create', job_type, null);
}

$.fn.zato.scheduler.execute = function(id) {

    var callback = function(data, status) {
        var success = status == 'success';
        if(success) {
            msg = 'Request submitted, check the server logs for details'; 
        }
        else {
            msg = data.responseText; 
        }
        $.fn.zato.user_message(success, msg);
    }

    var url = String.format('./execute/{0}/cluster/{1}/', id, $('#cluster_id').val());
    $.fn.zato.post(url, callback);

}

$.fn.zato.scheduler.edit = function(job_type, id) {
    $.fn.zato.scheduler._create_edit('edit', job_type, id);
}

$.fn.zato.scheduler.delete_ = function(id) {

    $.fn.zato.data_table.delete_(id, 'td.job_id_', 
        'Job [{0}] deleted', 'Are you sure you want to delete the job [{0}]?',
        true);
}
