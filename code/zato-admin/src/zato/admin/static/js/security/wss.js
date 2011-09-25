
// /////////////////////////////////////////////////////////////////////////////

// A base class for representing a WS-Security definition
var WSS = Class.create({
    initialize: function() {
        this.id = null;
        this.cluster_id = null;
        this.name = null;
        this.is_active = null;
        this.username = null;
        this.reject_empty_nonce_ts = null;
        this.reject_stale_username = null;
        this.expiry_limit = null;
        this.nonce_freshness = null;

    }
});

// A nicer toString.
WSS.prototype.toString = function() {
    return "<WSS\
        id=[" + this.cluster_id + "]\
        cluster_id=[" + this.cluster_id + "]\
        name=[" + this.name + "]\
        is_active=[" + this.is_active + "]\
        username=[" + this.username + "]\
        reject_empty_nonce_ts=[" + this.reject_empty_nonce_ts + "]\
        reject_stale_username=[" + this.reject_stale_username + "]\
        expiry_limit=[" + this.expiry_limit + "]\
        nonce_freshness=[" + this.nonce_freshness + "]\
    >";
};

WSS.prototype.boolean_html = function(attr) {
    return attr ? "Yes": "No";
}

// Dumps properties in a form suitable for creating a new data table row.
WSS.prototype.to_record = function() {
    var record = new Array();
    
    record["selection"] = "<input type='checkbox' />";
    record["name"] = this.name;
    record["is_active"] = this.boolean_html(this.is_active);
    record["username"] = this.username;
    record["reject_empty_nonce_ts"] = this.boolean_html(this.reject_empty_nonce_ts);
    record["reject_stale_username"] = this.boolean_html(this.reject_stale_username);
    record["expiry_limit"] = this.expiry_limit;
    record["nonce_freshness"] = this.nonce_freshness;
    
    record["edit"] = String.format("<a href=\"javascript:wss_edit('{0}')\">Edit</a>", this.id);
    record["change_password"] = String.format("<a href=\"javascript:wss_change_password('{0}')\">Change password</a>", this.id);
    record["delete"] = String.format("<a href=\"javascript:wss_delete('{0}')\">Delete</a>", this.id);

    return record;
};

WSS.prototype.add_row = function(wss, data_dt) {

    var add_at_idx = 0;
    data_dt.addRow(wss.to_record(), add_at_idx);
    
    var added_record = data_dt.getRecord(add_at_idx);
    
    added_record.setData("id", wss.id);
    added_record.setData("name", wss.name);
    added_record.setData("is_active", wss.is_active);
    added_record.setData("username", wss.username);
    added_record.setData("reject_empty_nonce_ts", wss.reject_empty_nonce_ts);
    added_record.setData("reject_stale_username", wss.reject_stale_username);
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
        
        wss.id = o.responseText;
        wss.cluster_id = $("id_cluster").value;
        wss.name = $("id_name").value;
        wss.is_active = $F("id_is_active") == "on";
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


// /////////////////////////////////////////////////////////////////////////////

function wss_create(cluster_id) {

    // Set up the form validation if necessary.
    if(typeof create_validation == "undefined") {
        create_validation = new Validation("create-form");
    }
    create_validation.reset();
    create_dialog.show();
}

// /////////////////////////////////////////////////////////////////////////////

YAHOO.util.Event.onDOMReady(function() {
    setup_create_dialog();
    //setup_edit_dialog();
    //setup_change_password_dialog();
    //setup_delete_dialog();
});