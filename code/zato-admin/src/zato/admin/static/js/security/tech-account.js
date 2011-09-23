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
    
    this_id = this.id ? this.ud : "";
    
    record["selection"] = "<input type='checkbox' />";
    record["name"] = this.name;
    record["is_active"] = this.is_active_html();
    
    record["edit"] = "<a href=\"javascript:tech_account_edit('"+ this_id +"', '"+ this.name +"', '"+ this.cluster_id +"')\">Edit</a>"
    record["change_password"] = "<a href=\"javascript:tech_account_change_password('"+ this_id +"', '"+ this.name +"', '"+ this.cluster_id +"')\">Change password</a>"
    record["delete"] = "<a href=\"javascript:tech_account_delete('"+ this_id +"', '"+ this.name +"', '"+ this.cluster_id +"')\">Delete</a>"

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
        tech_account.cluster_id = $("id_cluster").value;
        tech_account.name = $("id_name").value;
        tech_account.is_active = $F("id_is_active") == "on";
        tech_account.add_row(tech_account, data_dt);
        
        // Hide the dialog and confirm the changes have been saved.
        create_dialog.hide();

        update_user_message(true, "Succesfully created a new technical account, don't forget to set its password now");

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

function tech_account_create(cluster_id) {

    // Set up the form validation if necessary.
    if(typeof create_validation == "undefined") {
        create_validation = new Validation("create-form");
    }
    create_validation.reset();
    create_dialog.show();
}

YAHOO.util.Event.onDOMReady(function() {
    setup_create_dialog();
    //setup_edit_dialog();
    //setup_delete_dialog();
});