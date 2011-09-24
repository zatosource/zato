// A base class for representing a technical account
var TechnicalAccount = Class.create({
    initialize: function() {
        this.cluster_id = null;
        this.name = null;
        this.is_active = null;

    }
});

// A nicer toString.
TechnicalAccount.prototype.toString = function() {
    return "<TechnicalAccount\
 cluster_id=[" + this.cluster_id + "]\
 name=[" + this.name + "]\
 is_active=[" + this.is_active + "]\
>";
};

// Dumps properties in a form suitable for creating a new data table row.
TechnicalAccount.prototype.to_record = function() {
    var record = new Array();
    
    record["selection"] = "<input type='checkbox' />";
    record["name"] = this.name;
    record["is_active"] = this.is_active_html();
    
    record["edit"] = String.format("<a href=\"javascript:tech_account_edit('{0}')\">Edit</a>", this.id);
    record["change_password"] = String.format("<a href=\"javascript:tech_account_change_password('{0}')\">Change password</a>", this.id);
    record["delete"] = String.format("<a href=\"javascript:tech_account_delete('{0}')\">Delete</a>", this.id);

    return record;
};

TechnicalAccount.prototype.is_active_html = function() {
    return this.is_active ? "Yes": "No";
}

// /////////////////////////////////////////////////////////////////////////////

TechnicalAccount.prototype.add_row = function(tech_account, data_dt) {

    var add_at_idx = 0;
    data_dt.addRow(tech_account.to_record(), add_at_idx);
    
    var added_record = data_dt.getRecord(add_at_idx);
    
    added_record.setData("tech_account_id", tech_account.id);
    added_record.setData("name", tech_account.name);
    added_record.setData("is_active", tech_account.is_active_html());

}

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

        var tech_account = new TechnicalAccount();
        
        tech_account.id = o.responseText;
        tech_account.cluster_id = $("id_cluster").value;
        tech_account.name = $("id_name").value;
        tech_account.is_active = $F("id_is_active") == "on";
        tech_account.add_row(tech_account, data_dt);
        
        // Hide the dialog and confirm the changes have been saved.
        create_dialog.hide();

        update_user_message(true, "Succesfully created a new technical account, don't forget to update its password now");

        // Cleanup after work.
        create_cleanup();

    };

    var on_create_failure = function(o) {
        create_cleanup();
        update_user_message(false, o.responseText);
        create_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("create-tech-account", "yui-pe-content");

    // Instantiate the dialog.
    create_dialog = new YAHOO.widget.Dialog("create-tech-account",
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
            var tech_account_id = record.getData("tech_account_id");
            if(tech_account_id && tech_account_id == $("id_edit-tech_account_id").value) {

                var is_active = $F("id_edit-is_active") ? "Yes": "No";
                
                record.setData("name", $("id_edit-name").value);
                record.setData("is_active", is_active);
                
                data_dt.render();
            }
        }

        update_user_message(true, "Succesfully updated the technical account");

        // Cleanup after work.
        edit_cleanup();

    };

    var on_edit_failure = function(o) {
        edit_cleanup();
        update_user_message(false, o.responseText);
        edit_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("edit-tech-account", "yui-pe-content");

    // Instantiate the dialog.
    edit_dialog = new YAHOO.widget.Dialog("edit-tech-account",
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
    YAHOO.util.Dom.removeClass("change-password-tech-account", "yui-pe-content");

    // Instantiate the dialog.
    change_password_dialog = new YAHOO.widget.Dialog("change-password-tech-account",
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

// /////////////////////////////////////////////////////////////////////////////

function tech_account_create(cluster_id) {

    // Set up the form validation if necessary.
    if(typeof create_validation == "undefined") {
        create_validation = new Validation("create-form");
    }
    create_validation.reset();
    create_dialog.show();
}

function tech_account_edit(tech_account_id) {

    // Set up the form validation if necessary.
    if(typeof edit_validation == "undefined") {
        edit_validation = new Validation("edit-form");
    }
    edit_validation.reset();

    // Get the account's details from DB.

    var on_get_tech_account_success = function(o) {
        
        var json = YAHOO.lang.JSON.parse(o.responseText);
        var tech_account = json[0].fields;

        $("id_edit-tech_account_id").value = json[0].pk;
        $("id_edit-name").value = tech_account.name;
        $("id_edit-cluster_id").value = $("cluster_id").value;

        var checkbox_value = tech_account.is_active ? 'on': '';
        $("id_edit-is_active").setValue(checkbox_value);

        edit_dialog.show();
    };

    var on_get_tech_account_failure = function(o) {
        update_user_message(false, o.responseText);
    }

    var callback = {
        success: on_get_tech_account_success,
        failure: on_get_tech_account_failure,
    };
    
    var url = String.format("./get/by-id/{0}/cluster/{1}/", tech_account_id, $("cluster_id").value);
    YAHOO.util.Connect.asyncRequest("GET",  url, callback);
}

function tech_account_change_password(tech_account_id) {

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
        var tech_account_id_record = record.getData("tech_account_id");
        if(tech_account_id_record && tech_account_id == tech_account_id_record) {
            $("change-password-name").update(record.getData("name"));
            break;
        }
    }
    
    $("id_change_password-tech_account_id").setValue(tech_account_id);
    $("id_change_password-cluster_id").value = $("cluster_id").value;
    
    change_password_dialog.show();
}

// /////////////////////////////////////////////////////////////////////////////

YAHOO.util.Event.onDOMReady(function() {
    setup_create_dialog();
    setup_edit_dialog();
    setup_change_password_dialog();
});