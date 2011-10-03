
// A base class for representing a scheduler's job.
var Job = Class.create({
    initialize: function(record) {
        this.job_name = null;
        this.is_active = null;
        this.job_type = null;
        this.definition_text = null;

    }
});

// A nicer toString.
Job.prototype.toString = function() {
    return "<Job\
 job_name=[" + this.job_name + "]\
 is_active=[" + this.is_active + "]\
 job_type=[" + this.job_type + "]\
 definition_text=[" + this.definition_text + "]\
>";
};

// Dumps properties in a form suitable for creating a new data table row.
Job.prototype.to_record = function() {
    var record = new Array();
    record["job_name"] = this.job_name;
    record["job_type"] = friendly_names.get(this.job_type);
    record["definition_text"] = this.definition_text;
    record["service"] = this.service;
    record["edit"] = "";
    record["execute"] = "";
    record["delete"] = "";

    return record;
};

// /////////////////////////////////////////////////////////////////////////////
function dt_picker(input_id) {

    var year, month, day, hour, minute;
    var date_time = $(input_id).value;

    // It's okay if there's no value at all, it could be a 'create' action
    // currently being handled.
    if(date_time == '') {
        now = new Date();
        year = now.getFullYear();
        month = now.getMonth();
        day = now.getDay();
        hour = now.getHours();
        minute = now.getMinutes();
        second = now.getSeconds();
    }
    else {
        var date_time_splitted = date_time.split(" ");
        if(date_time_splitted.length != 2) {
            return; // What can we do..
        }

        var date_splitted = date_time_splitted[0].split("-");
        if(date_splitted.length != 3) {
            return; // Same as above..
        }

        year = parseInt(date_splitted[0]);
        month = parseInt(date_splitted[1]) - 1;
        day = parseInt(date_splitted[2]);

        var time_splitted = date_time_splitted[1].split(":");
        if(time_splitted.length != 3) {
            return; // Same as above..
        }

        hour = parseInt(time_splitted[0]);
        minute = parseInt(time_splitted[1]);
        second = parseInt(time_splitted[2]);

        var date_time_splitted = date_time.split(" ");
    }

    var picker_options = {
        time:true,
        year_range:10,
        minute_interval:1,
        initial_year: year,
        initial_month: month,
        initial_day: day,
        initial_hour: hour,
        initial_minute: minute,
        initial_second: second,
    }
    var calendar_date_select = new CalendarDateSelect($(input_id), picker_options);
}

// /////////////////////////////////////////////////////////////////////////////
// create
// /////////////////////////////////////////////////////////////////////////////

function create(job_type) {
    // Show the dialogs.
    
    if(job_type == 'one-time') {
        $('create-one_time').show();
        create_one_time_dialog.show();
    }
}

// /////////////////////////////////////////////////////////////////////////////

function setup_create_dialog_one_time() {
    var create_one_time_validation = new Validation('create-form-one_time');

    var on_submit = function() {
        if(create_one_time_validation.validate()) {
            // Submit the form if no errors have been found on the UI side.
            this.submit();
        }
    };

    var on_cancel = function() {
        this.cancel();
        create_one_time_dialog.hide();
        $('create-form-one_time').reset();
        create_one_time_validation.reset();
    };

    var on_success = function(o) {

        var job = new OneTimeJob(null);

        job.properties_from_form('id_create-one-time-');
        job.server_id = $('current_server_id').value;
        job.definition = o.responseText;

        data_dt.addRow(job.to_record());
        create_one_time_dialog.hide();
        $('create-form-one_time').reset();
        create_one_time_validation.reset();

        update_user_message(true, 'Successfully created job [' + job.job_name + '].');
    };

    var on_failure = function(o) {
        create_one_time_dialog.hide();
        $('create-form-one_time').reset();
        create_one_time_validation.reset();
        update_user_message(false, o.responseText);
    };

    // Instantiate the dialog if necessary.
    if(typeof create_one_time_dialog == 'undefined') {
        create_one_time_dialog = new YAHOO.widget.Dialog('create-one_time',
                                { width: '50em',
                                  fixedcenter: true,
                                  visible: false,
                                  draggable: true,
                                  postmethod: 'async',
                                  hideaftersubmit: false,
                                  constraintoviewport: true,
                                  buttons: [{text:'Submit', handler:on_submit},
                                            {text:'Cancel', handler:on_cancel, isDefault:true}]
                                });

        create_one_time_dialog.callback.success = on_success;
        create_one_time_dialog.callback.failure = on_failure;

        create_one_time_dialog.render();
    }
}


// /////////////////////////////////////////////////////////////////////////////

YAHOO.util.Event.onDOMReady(function() {

    Date.prototype.getPaddedHours = function() {
        var hour = this.getHours();
        if (hour < 10)
            hour = "0" + hour;
        return hour;
    }

    // Customize formatting of hours by adding a leading '0' if it's < 10
    Date.prototype.toFormattedString = function(include_time) {
        var hour;
        var str = this.getFullYear() + "-" + Date.padded2(this.getMonth() + 1) + "-" +Date.padded2(this.getDate());
        if (include_time) {
            hour = this.getHours();
            str += " " + this.getPaddedHours() + ":" + this.getPaddedMinutes() + ":00";
        }
        return str;
    };

    setup_create_dialog_one_time();
    //setup_edit_dialog();
    //setup_change_password_dialog();
    //setup_delete_dialog();
});

// /////////////////////////////////////////////////////////////////////////////

/*

// Populates the job's attributes basing on the values from a given record.
Job.prototype.set_properties = function(record) {
    var cols = data_dt.getColumnSet().keys;
    for(var x=0; x<cols.length; x++) {
        var col = cols[x];
        var data = record.getData(col.key);

        // Common attributes
        if(col.key == "job_name") {
            this.job_name = data;
        }
        else if(col.key == "job_type_raw"){
            this.job_type = data;
        }
        else if(col.key == "service"){
            this.service = data;
        }
        else if(col.key == "extra"){
            this.extra = data;
        }

        // One-time jobs only
        else if(col.key == "date_time_raw"){
            this.date_time_raw = data;
        }

        // Interval-based jobs only.
        else if(col.key == "start_date_raw"){
            this.start_date_raw = data;
        }
        else if(col.key == "weeks"){
            this.weeks = data;
        }
        else if(col.key == "days"){
            this.days = data;
        }
        else if(col.key == "hours"){
            this.hours = data;
        }
        else if(col.key == "minutes"){
            this.minutes = data;
        }
        else if(col.key == "seconds"){
            this.seconds = data;
        }
        else if(col.key == "repeat"){
            this.repeat = data;
        }
    }
}
// The reverse of Job.set_properties, updates a record with new job's values.
Job.prototype.update_record = function() {

    var new_values = new Hash();

    // Common attributes.
    new_values.set("job_name", this.job_name);
    new_values.set("job_type", friendly_names.get(this.job_type));
    new_values.set("definition", this.definition);
    new_values.set("service", this.service);
    new_values.set("extra", this.extra);

    // One-time jobs.
    new_values.set("date_time_raw", this.date_time_raw);

    // Interval-based jobs.
    new_values.set("start_date_raw", this.start_date_raw);
    new_values.set("weeks", this.weeks);
    new_values.set("days", this.days);
    new_values.set("hours", this.hours);
    new_values.set("minutes", this.minutes);
    new_values.set("seconds", this.seconds);
    new_values.set("repeat", this.repeat);

    var new_values_keys = new_values.keys();

    var cols = data_dt.getColumnSet().keys;
    for(var col_idx=0; col_idx<cols.length; col_idx++) {
        var col = cols[col_idx];
        for(var nv_idx=0; nv_idx<new_values_keys.length; nv_idx++) {
            var new_value_key = new_values_keys[nv_idx];
            var new_value = new_values.get(new_value_key);
            if(col.key == new_value_key && new_value) {
                this.record.setData(col.key, new_value);
                data_dt.updateCell(this.record, col.key, new_value);
            }
        }
    }
}


// Builds a delete URL for the current job.
Job.prototype.get_delete_url = function() {
    return "/zato/scheduler/delete/?job_name=" + this.job_name + "&server=" + this.server_id;
}

// Builds an execute URL for the current job.
Job.prototype.get_execute_url = function() {
    return ".?server=" + this.server_id;
}

// Builds an execute POST datafor the current job.
Job.prototype.get_execute_data = function() {
    return "zato_action=execute&job_name=" + this.job_name
}

// A specialized subclass for one-time jobs.
var OneTimeJob = Class.create(Job, {
    initialize: function($super, record) {
        $super(record);
        this.job_type = "one_time";
    },
    set_properties: function($super, record) {
        $super(record);
    },
});

OneTimeJob.prototype.properties_from_form = function(field_prefix) {

    // TODO: Should be moved to the base class.
    this.job_name = $(field_prefix + "job_name").value;
    this.service = $(field_prefix + "service").value;
    this.extra = $(field_prefix + "extra").value;

    this.date_time_raw = $(field_prefix + "date_time").value;
}

// A specialized subclass for interval-based jobs.
var IntervalBasedJob = Class.create(Job, {
    initialize: function($super, record) {
        $super(record);
        this.job_type = "interval_based";
    },
    set_properties: function($super, record) {
        $super(record);
    },
});

IntervalBasedJob.prototype.properties_from_form = function(field_prefix) {

    // TODO: Should be moved to the base class.
    this.job_name = $(field_prefix + "job_name").value;
    this.service = $(field_prefix + "service").value;
    this.extra = $(field_prefix + "extra").value;

    this.start_date_raw = $(field_prefix + "start_date").value;
    this.weeks = $(field_prefix + "weeks").value;
    this.days = $(field_prefix + "days").value;
    this.hours = $(field_prefix + "hours").value;
    this.minutes = $(field_prefix + "minutes").value;
    this.seconds = $(field_prefix + "seconds").value;
    this.repeat = $(field_prefix + "repeat").value;
}

// /////////////////////////////////////////////////////////////////////////////
//
// delete
//
// /////////////////////////////////////////////////////////////////////////////
function job_delete(job) {

    var on_success = function(o) {
        msg = "Successfully deleted job [" + job.job_name + "].";

        // Delete the row..
        data_dt.deleteRow(job.record);

        // .. and confirm everything went fine.
        update_user_message(true, msg);
    };

    var on_failure = function(o) {
        update_user_message(false, o.responseText);
    }

    var callback = {
        success: on_success,
        failure: on_failure,
    };

    var on_yes = function() {
        var transaction = YAHOO.util.Connect.asyncRequest("GET", job.get_delete_url(), callback);
        this.hide();
    };

    var on_no = function() {
        this.hide();
    };

    delete_dialog = new YAHOO.widget.SimpleDialog("delete_dialog", {
        width: "36em",
        effect:{
            effect: YAHOO.widget.ContainerEffect.FADE,
            duration: 0.10
        },
        fixedcenter: true,
        modal: false,
        visible: false,
        draggable: true
    });

    delete_dialog.setHeader("Are you sure?");
    delete_dialog.cfg.setProperty("icon", YAHOO.widget.SimpleDialog.ICON_WARN);

    var delete_buttons = [
        {text: "Yes", handler: on_yes},
        {text:"Cancel", handler: on_no, isDefault:true}
    ];

    delete_dialog.cfg.queueProperty("buttons", delete_buttons);
    delete_dialog.render(document.body);

    delete_dialog.setBody("Are you sure you want to delete job [" + job.job_name + "]?");
    delete_dialog.show();
}

// /////////////////////////////////////////////////////////////////////////////
//
// execute
//
// /////////////////////////////////////////////////////////////////////////////
function job_execute(job) {

    var on_execute_success = function(o) {
        update_user_message(true, "Request submitted, check the server's log for details.");
    };

    var on_execute_failure = function(o) {
        update_user_message(false, o.responseText);
    };

    var callback = {
      success: on_execute_success,
      failure: on_execute_failure,
    };

    var transaction = YAHOO.util.Connect.asyncRequest("POST", job.get_execute_url(),
        callback, job.get_execute_data());
}

// /////////////////////////////////////////////////////////////////////////////
//
// edit
//
// /////////////////////////////////////////////////////////////////////////////
function job_edit(job) {

    var edit_one_time_job = function(job) {
        var edit_one_time_validation = new Validation("edit-form-one_time", {immediate: true});

        var on_submit = function() {
            if(edit_one_time_validation.validate()) {
                // Submit the form if no errors have been found on the UI side.
                this.submit();
            }
        };

        var on_cancel = function() {
            this.cancel();
            edit_one_time_dialog.hide();
            $("edit-one_time").reset();
        };

        var on_success = function(o) {

            var record_id = o.argument;
            job.record = data_dt.getRecord(record_id);

            job.definition = o.responseText;
            job.properties_from_form("id_edit-one-time-");
            job.update_record();

            edit_one_time_dialog.hide();
            $("edit-form-one_time").reset();

            update_user_message(true, "Successfully saved the changes to job [" + job.job_name + "].");
        };

        var on_failure = function(o) {
            edit_one_time_dialog.hide();
            $("edit-form-one_time").reset();
            update_user_message(false, o.responseText);
        }

        var callback = {
            success: on_success,
            failure: on_failure,
        };

        // Instantiate the dialog if necessary.
        if(typeof edit_one_time_dialog == "undefined") {
            edit_one_time_dialog = new YAHOO.widget.Dialog("edit-one_time",
                                    { width: "50em",
                                      fixedcenter: true,
                                      visible: false,
                                      draggable: true,
                                      postmethod: "async",
                                      hideaftersubmit: false,
                                      constraintoviewport: true,
                                      buttons: [{text:"Submit", handler:on_submit},
                                                {text:"Cancel", handler:on_cancel, isDefault:true}]
                                    });

            edit_one_time_dialog.callback.success = on_success;
            edit_one_time_dialog.callback.failure = on_failure;

            edit_one_time_dialog.render();
        }

        edit_one_time_dialog.callback.argument = job.record.getId();

        // Populate the form.
        $("id_edit-one-time-job_name").value = job.job_name;
        $("id_edit-one-time-original_job_name").value = job.job_name;
        $("id_edit-one-time-date_time").value = job.date_time_raw;
        $("id_edit-one-time-service").value = job.service;
        $("id_edit-one-time-extra").value = job.extra;

        // Show the dialog.
        $("edit-one_time").show();
        edit_one_time_dialog.show();
    }

    var edit_interval_based_job = function(job) {
        var edit_interval_based_validation = new Validation("edit-form-interval_based", {immediate: true});

        var on_submit = function() {
            if(edit_interval_based_validation.validate()) {
                // Submit the form if no errors have been found on the UI side.
                this.submit();
            }
        };

        var on_cancel = function() {
            this.cancel();
            edit_interval_based_dialog.hide();
            $("edit-interval_based").reset();
        };

        var on_success = function(o) {

            var record_id = o.argument;
            job.record = data_dt.getRecord(record_id);

            job.definition = o.responseText;
            job.properties_from_form("id_edit-interval-based-");
            job.update_record();

            edit_interval_based_dialog.hide();
            $("edit-form-interval_based").reset();

            update_user_message(true, "Successfully saved the changes to job [" + job.job_name + "].");
        };

        var on_failure = function(o) {
            edit_interval_based_dialog.hide();
            $("edit-form-interval_based").reset();
            update_user_message(false, o.responseText);
        }

        var callback = {
            success: on_success,
            failure: on_failure,
        };

        // Instantiate the dialog if necessary.
        if(typeof edit_interval_based_dialog == "undefined") {
            edit_interval_based_dialog = new YAHOO.widget.Dialog("edit-interval_based",
                                    { width: "50em",
                                      fixedcenter: true,
                                      visible: false,
                                      draggable: true,
                                      postmethod: "async",
                                      hideaftersubmit: false,
                                      constraintoviewport: true,
                                      buttons: [{text:"Submit", handler:on_submit},
                                                {text:"Cancel", handler:on_cancel, isDefault:true}]
                                    });

            edit_interval_based_dialog.callback.success = on_success;
            edit_interval_based_dialog.callback.failure = on_failure;
            edit_interval_based_dialog.render();
        }

        edit_interval_based_dialog.callback.argument = job.record.getId();

        // Populate the form.
        $("id_edit-interval-based-job_name").value = job.job_name;
        $("id_edit-interval-based-original_job_name").value = job.job_name;
        $("id_edit-interval-based-start_date").value = job.start_date_raw;
        $("id_edit-interval-based-service").value = job.service;
        $("id_edit-interval-based-extra").value = job.extra;
        $("id_edit-interval-based-start_date").value = job.start_date_raw;
        $("id_edit-interval-based-weeks").value = job.weeks;
        $("id_edit-interval-based-days").value = job.days;
        $("id_edit-interval-based-hours").value = job.hours;
        $("id_edit-interval-based-minutes").value = job.minutes;
        $("id_edit-interval-based-seconds").value = job.seconds;
        $("id_edit-interval-based-repeat").value = job.repeat;

        // Show the dialog.
        $("edit-interval_based").show();
        edit_interval_based_dialog.show();
    }


    switch(job.job_type) {
        case 'one_time':
            edit_one_time_job(new OneTimeJob(job.record));
            return;
        case 'interval_based':
            edit_interval_based_job(new IntervalBasedJob(job.record));
            return;
    }
}

YAHOO.util.Event.onDOMReady(function() {

    // /////////////////////////////////////////////////////////////////////////
    //
    // Job creation context menu
    //
    // /////////////////////////////////////////////////////////////////////////
    var on_create_one_time = function() {
    };

    var on_create_interval_based = function() {

        var create_interval_based_validation = new Validation("create-form-interval_based", {immediate: true});

        var on_create_interval_based_submit = function() {
            if(create_interval_based_validation.validate()) {
                // Submit the form if no errors have been found on the UI side.
                this.submit();
            }
        };

        var on_create_interval_based_cancel = function() {
            this.cancel();
            create_interval_based_dialog.hide();
            $("create-form-interval_based").reset();
            create_interval_based_validation.reset();
        };

        var on_create_interval_based_success = function(o) {

            var job = new IntervalBasedJob(null);

            job.properties_from_form("id_create-interval-based-");
            job.definition = o.responseText;

            data_dt.addRow(job.to_record());
            create_interval_based_dialog.hide();
            $("create-form-interval_based").reset();
            create_interval_based_validation.reset();

            update_user_message(true, "Successfully created job [" + job.job_name + "].");
        };

        var on_create_interval_based_failure = function(o) {
            create_interval_based_dialog.hide();
            $("create-form-interval_based").reset();
            update_user_message(false, o.responseText);
            create_interval_based_validation.reset();
        };

        // Instantiate the dialog if necessary.
        if(typeof create_interval_based_dialog == "undefined") {
            create_interval_based_dialog = new YAHOO.widget.Dialog("create-interval_based",
                                    { width: "50em",
                                      fixedcenter: true,
                                      visible: false,
                                      draggable: true,
                                      postmethod: "async",
                                      hideaftersubmit: false,
                                      constraintoviewport: true,
                                      buttons: [{text:"Submit", handler:on_create_interval_based_submit},
                                                {text:"Cancel", handler:on_create_interval_based_cancel, isDefault:true}]
                                    });

            create_interval_based_dialog.callback.success = on_create_interval_based_success;
            create_interval_based_dialog.callback.failure = on_create_interval_based_failure;

            create_interval_based_dialog.render();
        }

        // Show the dialog.
        $("create-interval_based").show();
        create_interval_based_dialog.show();
    };

    var on_create_cron_style = function() {
        alert("Cron-style not implemented yet.");
    };

    var item_data = [
        {text: "One-time", onclick: {fn: on_create_one_time}},
        {text: "Interval-based", onclick: {fn: on_create_interval_based}},
        {text: "Cron-style", onclick: {fn: on_create_cron_style}},
    ];

    var create_menu = new YAHOO.widget.ContextMenu("create_menu", {
        trigger: $("create-link"),
        itemdata: item_data,
    });

    create_menu.render(document.body);

    // Hide dialogs on startup, after creating the menu.
    var dialogs = ["create-one_time", "create-interval_based", "edit-one_time", "edit-interval_based"];
    for(idx in dialogs) {
        $(dialogs[idx]).hide()
    }

});

function on_cell_click_event(args) {
    var target = args.target;
    var column = data_dt.getColumn(target);
    var record = data_dt.getRecord(target);

    var job = new Job(record);

     if(column.key == "delete") {
        job_delete(job);
     }
     else if(column.key == "execute") {
        job_execute(job);
     }
     else if(column.key == "edit") {
        job_edit(job);
     }
}

*/