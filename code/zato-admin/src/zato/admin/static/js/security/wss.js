
// /////////////////////////////////////////////////////////////////////////////

// A base class for representing a WS-Security definition
var WSS = Class.create({
    initialize: function() {
        this.id = null;
        this.cluster_id = null;
        this.name = null;
        this.is_active = null;
        this.username = null;
        this.password_type = null;
        this.password_type_raw = null;
        this.reject_empty_nonce_ts = null;
        this.reject_stale_username = null;
        this.expiry_limit = null;
        this.nonce_freshness = null;

    }
});

// A nicer toString.
WSS.prototype.toString = function() {
    return "<WSS\
        id=[" + this.id + "]\
        cluster_id=[" + this.cluster_id + "]\
        name=[" + this.name + "]\
        is_active=[" + this.is_active + "]\
        username=[" + this.username + "]\
        password_type_raw=[" + this.password_type_raw + "]\
        password_type=[" + this.password_type + "]\
        reject_empty_nonce_ts=[" + this.reject_empty_nonce_ts + "]\
        reject_stale_username=[" + this.reject_stale_username + "]\
        expiry_limit=[" + this.expiry_limit + "]\
        nonce_freshness=[" + this.nonce_freshness + "]\
    >";
};

WSS.prototype.boolean_html = function(attr) {
    return attr ? "Yes": "No";
}

WSS.prototype.boolean_html_reject = function(attr) {
    return attr ? "Yes": "No";
}

// Dumps properties in a form suitable for creating a new data table row.
WSS.prototype.to_record = function() {
    var record = new Array();
    
    record["selection"] = "<input type='checkbox' />";
    record["name"] = this.name;
    record["is_active"] = this.boolean_html(this.is_active);
    record["is_active_text"] = this.boolean_html(this.is_active);
    record["username"] = this.username;
    record["password_type_raw"] = this.password_type_raw;
    record["password_type"] = this.password_type;
    record["reject_empty_nonce_ts"] = this.reject_empty_nonce_ts;
    record["reject_empty_nonce_ts_text"] = this.boolean_html_reject(this.reject_empty_nonce_ts);
    record["reject_stale_username"] = this.reject_stale_username;
    record["reject_stale_username_text"] = this.boolean_html_reject(this.reject_stale_username);
    record["expiry_limit"] = this.expiry_limit;
    record["nonce_freshness"] = this.nonce_freshness;
    
    record["edit"] = String.format("<a href=\"javascript:edit('{0}')\">Edit</a>", this.id);
    record["change_password"] = String.format("<a href=\"javascript:change_password('{0}')\">Change password</a>", this.id);
    record["delete"] = String.format("<a href=\"javascript:delete_('{0}')\">Delete</a>", this.id);

    return record;
};

WSS.prototype.add_row = function(wss, data_dt) {

    var add_at_idx = 0;
    data_dt.addRow(wss.to_record(), add_at_idx);
    
    var added_record = data_dt.getRecord(add_at_idx);
    
    added_record.setData("wss_id", wss.id);
    added_record.setData("name", wss.name);
    added_record.setData("is_active", wss.is_active);
    added_record.setData("is_active_text", wss.boolean_html(wss.is_active));
    added_record.setData("username", wss.username);
    added_record.setData("password_type", wss.password_type);
    added_record.setData("password_type_raw", wss.password_type_raw);
    added_record.setData("reject_empty_nonce_ts", wss.reject_empty_nonce_ts);
    added_record.setData("reject_empty_nonce_ts_text", wss.boolean_html_reject(wss.reject_empty_nonce_ts));
    added_record.setData("reject_stale_username", wss.reject_stale_username);
    added_record.setData("reject_stale_username_text", wss.boolean_html_reject(wss.reject_stale_username));
    added_record.setData("expiry_limit", wss.expiry_limit);
    added_record.setData("nonce_freshness", wss.nonce_freshness);

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

        var wss = new WSS();
        var json = YAHOO.lang.JSON.parse(o.responseText);
        
        wss.id = json.pk;
        wss.cluster_id = $("id_cluster").value;
        wss.name = $("id_name").value;
        wss.is_active = $F("id_is_active") == "on";
        wss.password_type_raw = json.fields.password_type_raw;
        wss.password_type = json.fields.password_type;
        wss.username = $("id_username").value;
        wss.reject_empty_nonce_ts = $F("id_reject_empty_nonce_ts") == "on";
        wss.reject_stale_username = $F("id_reject_stale_username") == "on";
        wss.expiry_limit = $("id_expiry_limit").value;
        wss.nonce_freshness = $("id_nonce_freshness").value;
        wss.add_row(wss, data_dt);
        
        // Hide the dialog and confirm the changes have been saved.
        create_dialog.hide();

        update_user_message(true, "Succesfully created a new WS-Security definition, don't forget to update its password now");

        // Cleanup after work.
        create_cleanup();

    };

    var on_create_failure = function(o) {
        create_cleanup();
        update_user_message(false, o.responseText);
        create_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("create-wss", "yui-pe-content");

    // Instantiate the dialog.
    create_dialog = new YAHOO.widget.Dialog("create-wss",
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
            var wss_id = record.getData("wss_id");
            if(wss_id && wss_id == $("id_edit-wss_id").value) {
            
                var is_active = $F("id_edit-is_active") == 'on';
                var reject_empty_nonce_ts = $F("id_edit-reject_empty_nonce_ts") == 'on';
                var reject_stale_username = $F("id_edit-reject_stale_username") == 'on';

                var password_type = $('id_edit-password_type')[$('id_edit-password_type').selectedIndex].text;
                
                record.setData("name", $("id_edit-name").value);
                record.setData("is_active", is_active);
                record.setData("is_active_text", is_active ? "Yes": "No");
                record.setData("password_type", password_type);
                record.setData("username", $("id_edit-username").value);
                record.setData("reject_empty_nonce_ts", reject_empty_nonce_ts);
                record.setData("reject_empty_nonce_ts_text", reject_empty_nonce_ts ? "Yes": "No");
                record.setData("reject_stale_username", reject_stale_username);
                record.setData("reject_stale_username_text", reject_stale_username ? "Yes": "No");
                record.setData("expiry_limit", $("id_edit-expiry_limit").value);
                record.setData("nonce_freshness", $("id_edit-nonce_freshness").value);
                
                data_dt.render();
            }
        }

        update_user_message(true, "Succesfully updated the WS-Security definition");

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
        msg = "Successfully deleted the WS-Security definition [" + current_delete_name + "]";

        // Delete the row..
        
        var records = data_dt.getRecordSet().getRecords();
        for (x=0; x < records.length; x++) {
            var record = records[x];
            var id_record = record.getData("wss_id");
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

function wss_create(cluster_id) {

    // Set up the form validation if necessary.
    if(typeof create_validation == "undefined") {
        create_validation = new Validation("create-form");
    }
    create_validation.reset();
    create_dialog.show();
}

function edit(wss_id) {

    // Set up the form validation if necessary.
    if(typeof edit_validation == "undefined") {
        edit_validation = new Validation("edit-form");
    }
    edit_validation.reset();
    
    $("id_edit-cluster_id").value = $("cluster_id").value;

    var records = data_dt.getRecordSet().getRecords();
    for (x=0; x < records.length; x++) {
        var record = records[x];
        var wss_id_record = record.getData("wss_id");
        if(wss_id_record && wss_id_record == wss_id) {
        
            is_active = to_bool(record.getData("is_active"));
            reject_empty_nonce_ts = to_bool(record.getData("reject_empty_nonce_ts"));
            reject_stale_username = to_bool(record.getData("reject_stale_username"));
            
            $("id_edit-wss_id").value = record.getData("wss_id");
            $("id_edit-name").value = record.getData("name");
            $("id_edit-is_active").setValue(is_active);
            $("id_edit-username").value = record.getData("username");
            $("id_edit-password_type").value = record.getData("password_type_raw");
            $("id_edit-reject_empty_nonce_ts").setValue(reject_empty_nonce_ts);
            $("id_edit-reject_stale_username").setValue(reject_stale_username);
            $("id_edit-expiry_limit").value = record.getData("expiry_limit");
            $("id_edit-nonce_freshness").value = record.getData("nonce_freshness");
        }
    }
    
    edit_dialog.show();
}

function change_password(wss_id) {

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
        var wss_id_record = record.getData("wss_id");
        if(wss_id_record && wss_id == wss_id_record) {
            $("change-password-name").update(record.getData("name"));
            break;
        }
    }
    
    $("id_change_password-wss_id").setValue(wss_id);
    $("id_change_password-cluster_id").value = $("cluster_id").value;
    
    change_password_dialog.show();
}

function delete_(wss_id) {

    current_delete_id = wss_id;
    
    var records = data_dt.getRecordSet().getRecords();
    for (x=0; x < records.length; x++) {
        var record = records[x];
        var id_record = record.getData("wss_id");
        if(id_record && wss_id == id_record) {
            current_delete_name = record.getData("name").strip();
            break;
        }
    }

    delete_dialog.setBody(String.format("Are you sure you want to delete the WS-Security definition [{0}]", current_delete_name));
    delete_dialog.show();
    
}

// /////////////////////////////////////////////////////////////////////////////

YAHOO.util.Event.onDOMReady(function() {
    setup_create_dialog();
    setup_edit_dialog();
    setup_change_password_dialog();
    setup_delete_dialog();
});