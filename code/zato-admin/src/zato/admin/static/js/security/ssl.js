
// /////////////////////////////////////////////////////////////////////////////

// A base class for representing an SSL/TLS definition
var SSLAuth = Class.create({
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
SSLAuth.prototype.toString = function() {
    return "<SSLAuth\
        id=[" + this.id + "]\
        cluster_id=[" + this.cluster_id + "]\
        name=[" + this.name + "]\
        is_active=[" + this.is_active + "]\
        username=[" + this.username + "]\
        domain=[" + this.domain + "]\
        password=[" + this.password + "]\
    >";
};

SSLAuth.prototype.boolean_html = function(attr) {
    return attr ? "Yes": "No";
}


// Dumps properties in a form suitable for creating a new data table row.
SSLAuth.prototype.to_record = function() {
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

SSLAuth.prototype.add_row = function(object, data_dt) {

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

    //$('ssl-def-value').removeClassName('required');
    
    create_validation.reset();
    $("create-form").reset();

    /* See comment for add_to_def for explanation */

    $('ssl-def-field').addClassName('required');
    $('ssl-def-value').addClassName('required');

    Validation.reset($('ssl-def-field'));
    Validation.reset($('ssl-def-value'));

    $('ssl-def-field').removeClassName('required');
    $('ssl-def-value').removeClassName('required');
    
    $$("tr[id^='ssl-def-row-']").each(function(elem) {
        elem.remove();
    })
    
    
}

function setup_create_dialog() {

    var on_create_submit = function() {
        if(create_validation.validate()) {
        
            var def_elems = $$('tr[id^="ssl-def-row-"]');
            
            // First let's check whether there's at least one field/value pair
            // in the definition.
            if(!(def_elems && def_elems.length)) {
                alert("There must be least one field/value pair added to the definition.");
                return;
            }
            else {
                // Submit the form if no errors have been found on the UI side.
                this.submit();
                create_validation.reset();
            }
        }
    };

    var on_create_cancel = function() {
        this.cancel();
        create_cleanup();
    };

    var on_create_success = function(o) {

    /*
        var object = new SSLAuth();
        var json = YAHOO.lang.JSON.parse(o.responseText);
        
        object.id = json.pk;
        object.cluster_id = $("id_cluster").value;
        object.name = $("id_name").value;
        object.is_active = $F("id_is_active") == "on";
        object.username = $("id_username").value;
        object.domain = $("id_domain").value;
        object.add_row(object, data_dt);
        */
        
        // Hide the dialog and confirm the changes have been saved.
        create_dialog.hide();

        update_user_message(true, "Succesfully created a new SSL/TLS definition");

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
                            { width: "79em",
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

function add_to_def() {

    /* The .addClassName/.removeClassName dance is required because we want
    add_to_def to validate only these two particular fields, not the whole form,
    and conversly, we don't want the 'Submit' button these very two buttons
    below because it's 100% fine they're empty when someone submits form */

    $('ssl-def-field').addClassName('required');
    $('ssl-def-value').addClassName('required');

    var valid_field = Validation.validate('ssl-def-field');
    var valid_value = Validation.validate('ssl-def-value');
    if(!(valid_field && valid_value)) {
        return;
    }

    $('ssl-def-field').removeClassName('required');
    $('ssl-def-value').removeClassName('required');
    
    /* Check for duplicate fields */
    var def_elems = $$('tr[id^="ssl-def-row-"]');
    var given = $('ssl-def-field').value.strip();
    for(var x=0; x<def_elems.length; x++) {
        if(def_elems[x].firstDescendant().innerHTML == given) {
            alert(String.format('Field [{0}] already exists in the definition', given));
            return;
        }
    }

    var on_success = function(o) {
        $('ssl-def-table').insert(o.responseText);
        $('ssl-def-field').clear();
        $('ssl-def-value').clear();
        $('ssl-def-field').focus();
    };

    var on_failure = function(o) {
        update_user_message(false, o.responseText);
    }

    var callback = {
        success: on_success,
        failure: on_failure,
    };

    var url = String.format('./format-item/');

    YAHOO.util.Connect.initHeader('X-CSRFToken', YAHOO.util.Cookie.get('csrftoken'));
    YAHOO.util.Connect.setForm($('create-form'));
    
    var transaction = YAHOO.util.Connect.asyncRequest('POST', url, callback);
    
}

function remove_from_def(id) {
    $('ssl-def-row-' + id).remove();
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

        update_user_message(true, "Succesfully updated the SSL/TLS definition");

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
// delete
////////////////////////////////////////////////////////////////////////////////

function setup_delete_dialog() {

    var on_success = function(o) {
        msg = "Successfully deleted the SSL/TLS definition [" + current_delete_name + "]";

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
        
            is_active = record.getData("is_active") ? 'on' : ''
            
            $("id_edit-id").value = record.getData("id");
            $("id_edit-name").value = record.getData("name");
            $("id_edit-is_active").setValue(is_active);
            $("id_edit-username").value = record.getData("username");
            $("id_edit-domain").value = record.getData("domain");
        }
    }
    
    edit_dialog.show();
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

    delete_dialog.setBody(String.format("Are you sure you want to delete the SSL/TLS definition [{0}]", current_delete_name));
    delete_dialog.show();
    
}

// /////////////////////////////////////////////////////////////////////////////

YAHOO.util.Event.onDOMReady(function() {
    setup_create_dialog();
    //setup_edit_dialog();
    setup_delete_dialog();
});