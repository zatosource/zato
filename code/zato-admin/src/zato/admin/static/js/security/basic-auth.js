
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.BasicAuth = new Class({
	toString: function() {
		var s = '<BasicAuth id:{0} name:{1} is_active:{2} username:{3} domain:{4}>';
		return String.format(s, this.id ? this.id : '(none)', 
								this.name ? this.name : '(none)', 
								this.is_active ? this.is_active : '(none)', 
								this.username ? this.username : '(none)',
								this.domain ? this.domain : '(none)');
	}
});

$(document).ready(function() { 
	$('#data-table').tablesorter(); 
	$.fn.zato.data_table.parse($.fn.zato.data_table.BasicAuth);
	
	var actions = ['create', 'edit'];

	/* Dynamically prepare pop-up windows.
	*/
	$.each(actions, function(ignored, action) {
		var form_id = String.format('#{0}-form', action);
		var div_id = String.format('#{0}-div', action);

		// Pop-up				
		$(div_id).dialog({
			autoOpen: false,
			width: '40em',
			close: function(e, ui) {
				$.fn.zato.data_table.reset_form(form_id);
			}
		});
	});
	
	/* Prepare the validators here so that it's all still a valid HTML
	   even with bValidator's custom attributes.
	*/

	var attrs = ['name', 'username', 'domain'];		
	var field_id = '';
	var form_id = '';
	
	$.each(['', 'edit'], function(ignored, action) {
		$.each(attrs, function(ignored, attr) {
			if(action) {
				field_id = String.format('#id_{0}', attr);
			}
			else {
				field_id = String.format('#id_{0}-{1}', action, attr);
			}
			
			$(field_id).attr('data-bvalidator', 'required');
			$(field_id).attr('data-bvalidator-msg', 'This is a required field');
		});
		
		// Doh, not exactly the cleanest approach.
		if(action) {
			form_id = '#edit-form';
		}
		else {
			form_id = '#create-form';
		}
		$(form_id).bValidator();
	});

	/* Assign form submition handlers.
	*/
	
	$.each(actions, function(ignored, action) {
		$('#'+ action +'-form').submit(function() {
			$.fn.zato.scheduler.data_table.on_submit(action);
			return false;
		});
	});
})

$.fn.zato.security.basic_auth._create_edit = function(action, id) {

	var title = 'Create a new HTTP Basic Auth definition';
		
	if(action == 'edit') {

		var form = $(String.format('#{0}-form', action));
		var name_prefix = action + '-';
		var id_prefix = String.format('#id_{0}', name_prefix);
		var instance = $.fn.zato.data_table.data[id];
		
		$.fn.zato.form.populate(form, instance, name_prefix, id_prefix);
	}

	var div = $(String.format('#{0}-div', action));
	div.prev().text(title); // prev() is a .ui-dialog-titlebar
	div.dialog('open');
}

$.fn.zato.security.basic_auth.create = function() {
	$.fn.zato.security.basic_auth._create_edit('create');
}

$.fn.zato.security.basic_auth.edit = function(id) {
	$.fn.zato.security.basic_auth._create_edit('edit', id);
}

$.fn.zato.security.basic_auth.data_table.on_submit_complete = function(data, status, 
	action) {

	if(status == 'success') {
		var json = $.parseJSON(data.responseText);
		var include_tr = true ? action == 'create' : false;
		var row = $.fn.zato.security.basic_auth.data_table.add_row(json, action, include_tr);
		if(action == 'create') {
			$('#data-table > tbody:last').prepend(row);
		}
		else {
			var tr = $('#tr_'+ json.id).html(row);
			tr.addClass('updated');
		}	
	}

	$.fn.zato.data_table._on_submit_complete(data, status);
	$.fn.zato.data_table.cleanup('#'+ action +'-form');
}

$.fn.zato.security.basic_auth.data_table.on_submit = function(action) {
	var form = $('#' + action +'-form');
	var callback = function(data, status) {
			return $.fn.zato.scheduler.data_table.on_submit_complete(data, 
				status, action);
		}
	return $.fn.zato.data_table._on_submit(form, callback);
}

$.fn.zato.security.basic_auth.data_table.new_row = function(item, data, include_tr) {
    var row = '';
	
	if(include_tr) {
		row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
	}
	
	row += "<td class='numbering'>&nbsp;</td>";
	row += "<td><input type='checkbox' /></td>";
	row += String.format('<td>{0}</td>', item.name);
	row += String.format('<td>{0}</td>', item.is_active ? 'Yes' : 'No');
	row += String.format('<td>{0}</td>', item.username);
	row += String.format('<td>{0}</td>', item.domain);
	row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.basic_auth.change_password({0})'>Change password</a>", item.id));
	row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.security.basic_auth.edit('{0}')\">Edit</a>", item.id));
	row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.security.basic_auth.delete_({0});'>Delete</a>", item.id));
	row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
	row += String.format("<td class='ignore'>{0}</td>", item.is_active);
	
	if(include_tr) {
		row += '</tr>';
	}
	
	return row;
}

$.fn.zato.security.basic_auth.data_table.add_row = function(data, action, include_tr) {

	var item = new $.fn.zato.data_table.BasicAuth();
	var form = $(String.format('#{0}-form', action));
	var prefix = action + '-';
	var name = '';
	var _columns = $.fn.zato.data_table.get_columns();
	
	$.each(form.serializeArray(), function(idx, elem) {
		name = elem.name.replace(prefix, '');
		item[name] = elem.value;
	})
	if(!item.id) {
		item.id = data.id;
	}
	
	item.is_active = $.fn.zato.to_bool(item.is_active);
	
	$.fn.zato.data_table.data[item.id] = item;
	return $.fn.zato.security.basic_auth.data_table.new_row(item, data, include_tr);
}

$.fn.zato.security.basic_auth.delete_ = function(id) {
	$.fn.zato.data_table.delete_(id, 'td.item_id_', 
		'HTTP Basic Auth definition [{0}] deleted', 
		'Are you sure you want to delete the HTTP Basic Auth definition [{0}]?');
}

/*

// /////////////////////////////////////////////////////////////////////////////

// A base class for representing an HTTP Basic Auth definition
var HTTPBasicAuth = Class.create({
    initialize: function() {
        this.id = null;
        this.cluster_id = null;
        this.name = null;
        this.is_active = null;
        this.username = null;
        this.domain = null;
        this.password = null;

    }
});

// A nicer toString.
HTTPBasicAuth.prototype.toString = function() {
    return "<HTTPBasicAuth\
        id=[" + this.id + "]\
        cluster_id=[" + this.cluster_id + "]\
        name=[" + this.name + "]\
        is_active=[" + this.is_active + "]\
        username=[" + this.username + "]\
        domain=[" + this.domain + "]\
        password=[" + this.password + "]\
    >";
};

HTTPBasicAuth.prototype.boolean_html = function(attr) {
    return attr ? "Yes": "No";
}


// Dumps properties in a form suitable for creating a new data table row.
HTTPBasicAuth.prototype.to_record = function() {
    var record = new Array();
    
    record["selection"] = "<input type='checkbox' />";
    record["name"] = this.name;
    record["is_active"] = this.boolean_html(this.is_active);
    record["username"] = this.username;
    record["domain"] = this.domain;
    
    record["edit"] = String.format("<a href=\"javascript:edit('{0}')\">Edit</a>", this.id);
    record["change_password"] = String.format("<a href=\"javascript:change_password('{0}')\">Change password</a>", this.id);
    record["delete"] = String.format("<a href=\"javascript:delete_('{0}')\">Delete</a>", this.id);

    return record;
};

HTTPBasicAuth.prototype.add_row = function(object, data_dt) {

    var add_at_idx = 0;
    data_dt.addRow(object.to_record(), add_at_idx);
    
    var added_record = data_dt.getRecord(add_at_idx);
    
    added_record.setData("id", object.id);
    added_record.setData("name", object.name);
    added_record.setData("is_active", object.is_active);
    added_record.setData("username", object.username);
    added_record.setData("domain", object.domain);

}

// /////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// create
////////////////////////////////////////////////////////////////////////////////
function create_cleanup() {
    create_validation.reset();
    $("create-form").reset();
}

function setup_create_dialog() {

    var on_create_submit = function() {
        if(create_validation.validate()) {
            // Submit the form if no errors have been found on the UI side.
            this.submit();
            create_validation.reset();
        }
    };

    var on_create_cancel = function() {
        this.cancel();
        create_cleanup();
    };

    var on_create_success = function(o) {

        var object = new HTTPBasicAuth();
        var json = YAHOO.lang.JSON.parse(o.responseText);
        
        object.id = json.pk;
        object.cluster_id = $("id_cluster").value;
        object.name = $("id_name").value;
        object.is_active = $F("id_is_active") == "on";
        object.username = $("id_username").value;
        object.domain = $("id_domain").value;
        object.add_row(object, data_dt);
        
        // Hide the dialog and confirm the changes have been saved.
        create_dialog.hide();

        update_user_message(true, "Succesfully created a new HTTP Basic Auth definition, don't forget to update its password now");

        // Cleanup after work.
        create_cleanup();

    };

    var on_create_failure = function(o) {
        create_cleanup();
        update_user_message(false, o.responseText);
        create_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("create-div", "yui-pe-content");

    // Instantiate the dialog.
    create_dialog = new YAHOO.widget.Dialog("create-div",
                            { width: "39em",
                              fixedcenter: true,
                              visible: false,
                              draggable: true,
                              postmethod: "async",
                              hideaftersubmit: false,
                              constraintoviewport: true,
                              buttons: [{text:"Submit", handler:on_create_submit},
                                        {text:"Cancel", handler:on_create_cancel, isDefault:true}]
                            });

    create_dialog.callback.success = on_create_success;
    create_dialog.callback.failure = on_create_failure;

    // Render the dialog.
    create_dialog.render();
}

////////////////////////////////////////////////////////////////////////////////
// edit
////////////////////////////////////////////////////////////////////////////////
function edit_cleanup() {
    edit_validation.reset();
    $("edit-form").reset();
}

function setup_edit_dialog() {

    var on_edit_submit = function() {
        if(edit_validation.validate()) {
            // Submit the form if no errors have been found on the UI side.
            this.submit();
            edit_validation.reset();
        }
    };

    var on_edit_cancel = function() {
        this.cancel();
        edit_cleanup();
    };

    var on_edit_success = function(o) {

        edit_dialog.hide();
        
        var records = data_dt.getRecordSet().getRecords();
        for (x=0; x < records.length; x++) {
            var record = records[x];
            var id = record.getData("id");
            if(id && id == $("id_edit-id").value) {

                var is_active = $F("id_edit-is_active") ? "Yes": "No";
                record.setData("name", $("id_edit-name").value);
                record.setData("is_active", is_active);
                record.setData("username", $("id_edit-username").value);
                record.setData("domain", $("id_edit-domain").value);
                
                data_dt.render();
            }
        }

        update_user_message(true, "Succesfully updated the HTTP Basic Auth definition");

        // Cleanup after work.
        edit_cleanup();

    };

    var on_edit_failure = function(o) {
        edit_cleanup();
        update_user_message(false, o.responseText);
        edit_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("edit-form", "yui-pe-content");

    // Instantiate the dialog.
    edit_dialog = new YAHOO.widget.Dialog("edit-div",
                            { width: "39em",
                              fixedcenter: true,
                              visible: false,
                              draggable: true,
                              postmethod: "async",
                              hideaftersubmit: false,
                              constraintoviewport: true,
                              buttons: [{text:"Submit", handler:on_edit_submit},
                                        {text:"Cancel", handler:on_edit_cancel, isDefault:true}]
                            });

    edit_dialog.callback.success = on_edit_success;
    edit_dialog.callback.failure = on_edit_failure;

    // Render the dialog.
    edit_dialog.render();
}

////////////////////////////////////////////////////////////////////////////////
// change_password
////////////////////////////////////////////////////////////////////////////////
function change_password_cleanup() {
    change_password_validation.reset();
    $("change-password-form").reset();
}

function setup_change_password_dialog() {

    var on_change_password_submit = function() {
        if(change_password_validation.validate()) {
            // Submit the form if no errors have been found on the UI side.
            this.submit();
            change_password_validation.reset();
        }
    };

    var on_change_password_cancel = function() {
        this.cancel();
        change_password_cleanup();
    };

    var on_change_password_success = function(o) {

        change_password_dialog.hide();
        update_user_message(true, "Succesfully updated the password");

        // Cleanup after work.
        change_password_cleanup();

    };

    var on_change_password_failure = function(o) {
        change_password_cleanup();
        update_user_message(false, o.responseText);
        change_password_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("change-password", "yui-pe-content");

    // Instantiate the dialog.
    change_password_dialog = new YAHOO.widget.Dialog("change-password",
                            { width: "39em",
                              fixedcenter: true,
                              visible: false,
                              draggable: true,
                              postmethod: "async",
                              hideaftersubmit: false,
                              constraintoviewport: true,
                              buttons: [{text:"Submit", handler:on_change_password_submit},
                                        {text:"Cancel", handler:on_change_password_cancel, isDefault:true}]
                            });

    change_password_dialog.callback.success = on_change_password_success;
    change_password_dialog.callback.failure = on_change_password_failure;

    // Render the dialog.
    change_password_dialog.render();
}

////////////////////////////////////////////////////////////////////////////////
// delete
////////////////////////////////////////////////////////////////////////////////

function setup_delete_dialog() {

    var on_success = function(o) {
        msg = "Successfully deleted the HTTP Basic Auth definition [" + current_delete_name + "]";

        // Delete the row..
        
        var records = data_dt.getRecordSet().getRecords();
        for (x=0; x < records.length; x++) {
            var record = records[x];
            var id_record = record.getData("id");
            if(id_record && current_delete_id == id_record) {
                data_dt.deleteRow(x);
                break;
            }
        }


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

        var url = String.format("./delete/{0}/cluster/{1}/", current_delete_id, $("cluster_id").value);

        YAHOO.util.Connect.initHeader('X-CSRFToken', YAHOO.util.Cookie.get("csrftoken"));
        var transaction = YAHOO.util.Connect.asyncRequest("POST", url, callback);

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

};

// /////////////////////////////////////////////////////////////////////////////

function create(cluster_id) {

    // Set up the form validation if necessary.
    if(typeof create_validation == "undefined") {
        create_validation = new Validation("create-form");
    }
    create_validation.reset();
    create_dialog.show();
}

function edit(id) {

    // Set up the form validation if necessary.
    if(typeof edit_validation == "undefined") {
        edit_validation = new Validation("edit-form");
    }
    edit_validation.reset();
    
    $("id_edit-cluster_id").value = $("cluster_id").value;

    var records = data_dt.getRecordSet().getRecords();
    for (x=0; x < records.length; x++) {
        var record = records[x];
        var id_record = record.getData("id");
        if(id_record && id_record == id) {
        
			// TODO: This == 'Yes' thing isn't exactly anything like it should be done.
			var is_active = record.getData('is_active') == 'Yes' ? 'on' : ''
            
            $("id_edit-id").value = record.getData("id");
            $("id_edit-name").value = record.getData("name");
            $("id_edit-is_active").setValue(is_active);
            $("id_edit-username").value = record.getData("username");
            $("id_edit-domain").value = record.getData("domain");
        }
    }
    
    edit_dialog.show();
}

function change_password(id) {

    // Set up the form validation if necessary.
    if(typeof change_password_validation == "undefined") {
        change_password_validation = new Validation("change-password-form");

        Validation.add("validate-password-confirm", "Passwords need to be the same",
                       {equalToField:"id_password1"});
        
    }
    change_password_validation.reset();

    var records = data_dt.getRecordSet().getRecords();
    for (x=0; x < records.length; x++) {
        var record = records[x];
        var id_record = record.getData("id");
        if(id_record && id == id_record) {
            $("change-password-name").update(record.getData("name"));
            break;
        }
    }
    
    $("id_change_password-id").setValue(id);
    $("id_change_password-cluster_id").value = $("cluster_id").value;
    
    change_password_dialog.show();
}

function delete_(id) {

    current_delete_id = id;
    
    var records = data_dt.getRecordSet().getRecords();
    for (x=0; x < records.length; x++) {
        var record = records[x];
        var id_record = record.getData("id");
        if(id_record && id == id_record) {
            current_delete_name = record.getData("name").strip();
            break;
        }
    }

    delete_dialog.setBody(String.format("Are you sure you want to delete the HTTP Basic Auth definition [{0}]", current_delete_name));
    delete_dialog.show();
    
}

// /////////////////////////////////////////////////////////////////////////////

YAHOO.util.Event.onDOMReady(function() {
    setup_create_dialog();
    setup_edit_dialog();
    setup_change_password_dialog();
    setup_delete_dialog();
});

*/