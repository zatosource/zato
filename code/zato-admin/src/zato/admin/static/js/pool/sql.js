
// List of all attributes which can be manipulated through an edit form.
edit_attrs = ["original_pool_name", "pool_name", "engine", "host", "db_name", "user", "pool_size", "extra"];

//
// edit
//
function edit_cleanup() {
    edit_validation.reset();
    $("edit-form").reset();
}

function setup_edit_dialog() {
    var on_edit_submit = function() {
        if(edit_validation.validate()) {
            // Submit the form if no errors have been found on the UI side.
            this.submit();
        }
    };

    var on_edit_cancel = function() {
        this.cancel();
        edit_cleanup();
    };

    var on_edit_success = function(o) {

        for(var x=0; x<edit_attrs.length; x++) {
            var attr = edit_attrs[x];
            var new_value = $("id_edit-" + attr).value;
            var hidden_value = new_value;

            // DB type is shown by its friendly name.
            if(attr == "engine") {
                new_value = engine_friendly_name.get(new_value);
            }

            // Update the business values..
            if(attr != "original_pool_name") {
                if(attr == "extra") {
                    $(attr + "_" + current_temp_id).innerHTML = "<pre>" + new_value + "</pre>";
                }
                else {
                    $(attr + "_" + current_temp_id).innerHTML = new_value;
                }
            }

            // .. and the hidden ones as well.
            if(attr == "original_pool_name") {
                hidden_value = $("id_edit-pool_name").value;
            }

            $("hidden_" + attr + "_" + current_temp_id).value = hidden_value;
        }

        // Hide the dialog and confirm the changes have been saved.
        edit_dialog.hide();

        update_user_message(true, "Succesfully saved the changes");

        // Cleanup after work.
        edit_cleanup();
    };

    var on_edit_failure = function(o) {
        edit_dialog.hide();
        update_user_message(false, o.responseText);
        edit_cleanup();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("edit-sql", "yui-pe-content");

    // Instantiate the dialog.
    edit_dialog = new YAHOO.widget.Dialog("edit-sql",
                            { width: "35em",
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
};

//
// create
//
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

        // Create a new row and a hidden form.
        var new_row = new Array();
        var new_hidden_form_elems = new Array();

        // Get the new row's temporary ID.
        var temp_id = get_random_string();

        var new_value;

        // Prepare the values of a row and of a hidden form..
        for(var x=0; x<edit_attrs.length; x++) {
            var attr = edit_attrs[x];

            // No 'original_pool_name' when the pool is first created.
            if(attr == "original_pool_name") {
                new_value =  $("id_pool_name").value;
            }
            else {
                new_value = $("id_" + attr).value;
            }

            // Hidden form fields.
            var hidden_field_value = "<input type='hidden' id='hidden_" + attr + "_" + temp_id + "' value='" + new_value + "'/>";
            new_hidden_form_elems.push(hidden_field_value);

            // DB type is shown by its friendly name.
            if(attr == "engine") {
                new_value = engine_friendly_name.get(new_value);
            }

            if(attr == "extra") {
                new_value = "<pre>" + new_value + "</pre>";
            }

            // Business values.
            var new_span_value = "<span id=" + attr + "_" + temp_id +">" + new_value + "</span>";
            new_row[attr] = new_span_value;

        }

        // .. the hidden form containing all new values ..
        var hidden_form = "<form style='display:none'>";
        hidden_form += new_hidden_form_elems.join("\n");
        hidden_form += "</form>";

        // Arbitrarily pick an element from a new row and append the hidden form to it.
        new_row["pool_name"] += hidden_form;

        // .. Javascript links ..
        new_row["edit"] = "<a href=\"javascript:sql_edit('" + temp_id + "')\">Edit</a>";
        new_row["change_password"] = "<a href=\"javascript:sql_change_password('" + temp_id + "')\">Change password</a>";
        new_row["ping"] = "<a href=\"javascript:sql_ping('" + temp_id + "', '" + current_server_id + "')\">Ping</a>";
        new_row["delete"] = "<a href=\"javascript:sql_delete('" + temp_id + "', '" + current_server_id + "')\">Delete</a>";

        // .. and show it on the UI.
        data_dt.addRow(new_row);

        // Hide the dialog and confirm the changes have been saved.
        create_dialog.hide();

        update_user_message(true, "Succesfully created a new SQL connection pool. Don't forget to set its password.");

        // Cleanup after work.
        create_cleanup();

    };

    var on_create_failure = function(o) {
        create_cleanup();
        update_user_message(false, o.responseText);
        create_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("create-sql", "yui-pe-content");

    // Instantiate the dialog.
    create_dialog = new YAHOO.widget.Dialog("create-sql",
                            { width: "35em",
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

//
// change password
//
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
        change_password_cleanup();
        this.cancel();
    };

    var on_change_password_success = function(o) {

        // Hide the dialog and confirm the changes have been saved.
        change_password_dialog.hide();

        update_user_message(true, "Password changed");

        // Cleanup after work.
        change_password_cleanup();

    };

    var on_change_password_failure = function(o) {
        change_password_dialog.hide();
        change_password_cleanup();
        update_user_message(false, o.responseText);
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("change-password-sql", "yui-pe-content");

    // Instantiate the dialog.
    change_password_dialog = new YAHOO.widget.Dialog("change-password-sql",
                            { width: "35em",
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
};

function setup_delete_dialog() {

    var on_success = function(o) {
        msg = "Successfully deleted the SQL connection pool [" + current_delete_pool_name + "]";

        // Delete the row..
        var hidden_pool_name = $("hidden_pool_name_" + current_temp_id);
        data_dt.deleteRow(hidden_pool_name);

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

        var url = "/zato/pool/sql/delete/?pool_name=" + current_delete_pool_name + "&server=" + current_delete_server_id;
        var transaction = YAHOO.util.Connect.asyncRequest("GET", url, callback);

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

function sql_edit(temp_id) {

    current_temp_id = temp_id;

    // Set up the form validation if necessary.
    if(typeof edit_validation == "undefined") {
        edit_validation = new Validation("edit-form", {immediate: true});
    }
    edit_validation.reset();

    // Populate the edit form..
    for(var x=0; x<edit_attrs.length; x++) {
        var attr = edit_attrs[x];
        var current_hidden_elem_id = "hidden_" + attr + "_" + current_temp_id;
        var current_hidden_elem = $(current_hidden_elem_id);
        $("id_edit-" + attr).value = current_hidden_elem.value;
    }

    edit_dialog.show();
}

function sql_create(server_id) {
    current_server_id = server_id;

    // Set up the form validation if necessary.
    if(typeof create_validation == "undefined") {
        create_validation = new Validation("create-form");
    }
    create_validation.reset();
    create_dialog.show();
}

function sql_change_password(temp_id) {
    current_temp_id = temp_id;

    // Set up the form validation if necessary.
    if(typeof change_password_validation == "undefined") {
        change_password_validation = new Validation("change-password-form");
        Validation.add("validate-password-confirm", "Your confirmation password does not match the first password.",
                       {equalToField:"id_password1"});
    }

    // Set the pool's name.
    var pool_name = $("hidden_pool_name_" + current_temp_id).value;
    $("change_password_pool_name").innerHTML = pool_name;
    $("hidden_change_password_pool_name").value = pool_name;

    change_password_cleanup();
    change_password_validation.reset();
    change_password_dialog.show();

}

function sql_delete(temp_id, server_id) {
    current_temp_id = temp_id;
    var pool_name = $("hidden_pool_name_" + current_temp_id).value

    current_delete_pool_name = pool_name;
    current_delete_server_id = server_id;

    delete_dialog.setBody("Are you sure you want to delete the SQL connection pool [" + pool_name + "]?");
    delete_dialog.show();

}

function sql_ping(temp_id, server_id) {
    current_temp_id = temp_id;
    var pool_name = $("hidden_pool_name_" + current_temp_id).value

    var on_success = function(o) {
        update_user_message(true, o.responseText);
    };

    var on_failure = function(o) {
        update_user_message(false, o.responseText);
    }

    var callback = {
        cache:false,
        success: on_success,
        failure: on_failure,
    };

    var url = "/zato/pool/sql/ping/?pool_name=" + pool_name + "&server=" + server_id;
    var transaction = YAHOO.util.Connect.asyncRequest("GET", url, callback);

}

YAHOO.util.Event.onDOMReady(function() {
    setup_edit_dialog();
    setup_create_dialog();
    setup_change_password_dialog();
    setup_delete_dialog();
});