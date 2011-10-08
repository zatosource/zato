
// /////////////////////////////////////////////////////////////////////////////

// A base class for representing an SSL/TLS definition
var SSLAuth = Class.create({
    initialize: function() {
        this.id = null;
        this.name = null;
        this.is_active = null;
        this.definition_text = null;

    }
});

// A nicer toString.
SSLAuth.prototype.toString = function() {
    return '<SSLAuth\
        id=[' + this.id + ']\
        cluster_id=[' + this.cluster_id + ']\
        name=[' + this.name + ']\
        is_active=[' + this.is_active + ']\
        definition_text=[' + this.definition_text + ']\
    >';
};

SSLAuth.prototype.boolean_html = function(attr) {
    return attr ? 'Yes': 'No';
}


// Dumps properties in a form suitable for creating a new data table row.
SSLAuth.prototype.to_record = function() {
    var record = new Array();
    
    record['selection'] = "<input type='checkbox' />";
    record['name'] = this.name;
    record['is_active'] = this.boolean_html(this.is_active);
    record['definition_text'] = this.definition_text;
    
    record['edit'] = String.format("<a href='javascript:edit({0})'>Edit</a>", this.id);
    record['delete'] = String.format("<a href='javascript:delete_({0})'>Delete</a>", this.id);

    return record;
};

SSLAuth.prototype.add_row = function(object, data_dt) {

    var add_at_idx = 0;
    data_dt.addRow(object.to_record(), add_at_idx);
    
    var added_record = data_dt.getRecord(add_at_idx);
    
    added_record.setData('id', object.id);
    added_record.setData('name', object.name);
    added_record.setData('is_active', object.is_active);
    added_record.setData('definition_text', object.definition_text);

}

// /////////////////////////////////////////////////////////////////////////////

function clear_def_table() {
	/* Clears the table used for creating and editing of the definitions.
	Removes each 'tr' element, except for the one used for adding new 
	field/value pairs. */
	
    $$("tr[id^='ssl-def-row-']").each(function(elem) {
        elem.remove();
    })
}

// /////////////////////////////////////////////////////////////////////////////

function main_cleanup() {

    //$('ssl-def-value').removeClassName('required');
    
    main_validation.reset();
    $('main-form').reset();

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
    
    clear_def_table();
    
}

function setup_main_dialog() {

    var on_button_submit = function() {
        if(main_validation.validate()) {
        
            var def_elems = $$("tr[id^='ssl-def-row-']");
            
            // First let's check whether there's at least one field/value pair
            // in the definition.
            if(!(def_elems && def_elems.length)) {
                alert('There must be least one field/value pair added to the definition.');
                return;
            }
            else {
                // Submit the form if no errors have been found on the UI side.
                this.submit();
                main_validation.reset();
            }
        }
    };

    var on_button_cancel = function() {
        this.cancel();
        main_cleanup();
    };

    var on_button_success = function(o) {
	
		var json = YAHOO.lang.JSON.parse(o.responseText);

		if(current_action == 'create') {
			var object = new SSLAuth();
	
			object.id = json.pk;
			object.name = $('id_name').value;
			object.is_active = $F('id_is_active') == 'on';
			object.definition_text = json.definition_text
			object.add_row(object, data_dt);
		}
		else {
			var records = data_dt.getRecordSet().getRecords();
			for (x=0; x < records.length; x++) {
				var record = records[x];
				var id = record.getData('id');
				if(id && id == json.pk) {
	
					var is_active = $F('id_is_active') ? 'Yes': 'No';
					record.setData('name', $('id_name').value);
					record.setData('is_active', is_active);
					record.setData('definition_text', json.definition_text);
					
					data_dt.render();
				}
			}
		}
        
        // Hide the dialog and confirm the changes have been saved.
        main_dialog.hide();

		if(current_action == 'create') {
			success_msg = 'Succesfully created a new SSL/TLS definition';
		}
		else {
			success_msg = 'Succesfully updated the SSL/TLS definition';
		};

        update_user_message(true, success_msg);

        // Cleanup after work.
        main_cleanup();

    };

    var on_button_failure = function(o) {
		if(current_action == 'create') {
			main_cleanup();
		}
		else {
			edit_cleanup();
		}
		
        update_user_message(false, o.responseText);
        main_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass('form-div', 'yui-pe-content');

    // Instantiate the dialog.
    main_dialog = new YAHOO.widget.Dialog('form-div',
                            { width: '79em',
                              fixedcenter: true,
                              visible: false,
                              draggable: true,
                              postmethod: 'async',
                              hideaftersubmit: false,
                              constraintoviewport: true,
                              buttons: [{text:'Submit', handler:on_button_submit},
                                        {text:'Cancel', handler:on_button_cancel, isDefault:true}]
                            });

    main_dialog.callback.success = on_button_success;
    main_dialog.callback.failure = on_button_failure;

    // Render the dialog.
    main_dialog.render();
}

function add_to_def() {

    /* The .addClassName/.removeClassName dance is required because we want
    add_to_def to validate only these two particular fields, not the whole form,
    and conversly, we don't want the 'Submit' button to validate these two very 
	buttons below because it's 100% fine they're empty when someone submits 
	the form. */

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
    var def_elems = $$("tr[id^='ssl-def-row-']");
    var given = $('ssl-def-field').value.strip();
    for(var x=0; x<def_elems.length; x++) {
        if(def_elems[x].firstDescendant().innerHTML == given) {
            alert(String.format('Field [{0}] already exists in the definition', given));
            return;
        }
    }

    var on_success = function(o) {
        $('ssl-def-tbody').insert(o.responseText);
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

    var url = './format-item/'
    YAHOO.util.Connect.initHeader('X-CSRFToken', YAHOO.util.Cookie.get('csrftoken'));
    YAHOO.util.Connect.setForm($('main-form'));
    
    var transaction = YAHOO.util.Connect.asyncRequest('POST', url, callback);
    
}

function remove_from_def(id) {
    $('ssl-def-row-' + id).remove();
}

function setup_delete_dialog() {

    var on_success = function(o) {
        msg = 'Successfully deleted the SSL/TLS definition [' + current_delete_name + ']';

        // Delete the row..
        
        var records = data_dt.getRecordSet().getRecords();
        for (x=0; x < records.length; x++) {
            var record = records[x];
            var id_record = record.getData('id');
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

        var url = String.format('./delete/{0}/cluster/{1}/', current_delete_id, $('cluster_id').value);

        YAHOO.util.Connect.initHeader('X-CSRFToken', YAHOO.util.Cookie.get('csrftoken'));
        var transaction = YAHOO.util.Connect.asyncRequest('POST', url, callback);

        this.hide();
    };

    var on_no = function() {
        this.hide();
    };

    delete_dialog = new YAHOO.widget.SimpleDialog('delete_dialog', {
        width: '36em',
        effect:{
            effect: YAHOO.widget.ContainerEffect.FADE,
            duration: 0.10
        },
        fixedcenter: true,
        modal: false,
        visible: false,
        draggable: true
    });

    delete_dialog.setHeader('Are you sure?');
    delete_dialog.cfg.setProperty('icon', YAHOO.widget.SimpleDialog.ICON_WARN);

    var delete_buttons = [
        {text: 'Yes', handler: on_yes},
        {text:'Cancel', handler: on_no, isDefault:true}
    ];

    delete_dialog.cfg.queueProperty('buttons', delete_buttons);
    delete_dialog.render(document.body);

};

// /////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// create
////////////////////////////////////////////////////////////////////////////////

function create(cluster_id) {

	current_action = 'create';
	$('form-title').update('Create a new SSL/TLS definition');

    // Set up the form validation if necessary.
    if(typeof main_validation == 'undefined') {
        main_validation = new Validation('main-form');
    }

	main_cleanup();
    $('main-form').writeAttribute('action', './create/');
    main_validation.reset();
	clear_def_table();
    main_dialog.show();
}

////////////////////////////////////////////////////////////////////////////////
// edit
////////////////////////////////////////////////////////////////////////////////

function edit(id) {

	current_action = 'edit';
	$('form-title').update('Edit the SSL/TLS definition');

    // Set up the form validation if necessary.
    if(typeof main_validation == 'undefined') {
        main_validation = new Validation('main-form');
    }

	clear_def_table();
	$('ssl-def-tbody').insert("<tr id='ssl-def-row-loader'><td colspan='3' class='loader'><span><img src='/static/gfx/ajax-loader.gif'/> Please wait</span></td></tr>");
    $('main-form').writeAttribute('action', './edit/');
    main_validation.reset();
    
    cluster_id = $('cluster_id').value
    $('cluster_id').value = cluster_id;
	
    var records = data_dt.getRecordSet().getRecords();
    for (x=0; x < records.length; x++) {
        var record = records[x];
        var id_record = record.getData('id');
        if(id_record && id_record == id) {
        
            is_active = record.getData('is_active') == 'Yes' ? 'on' : ''
            
            $('id').value = id;
            $('id_name').value = record.getData('name');
            $('id_is_active').setValue(is_active);

            var on_success = function(o) {
				clear_def_table();
				$('ssl-def-tbody').insert(o.responseText);
            };
        
            var on_failure = function(o) {
                update_user_message(false, o.responseText);
            }
        
            var callback = {
                success: on_success,
                failure: on_failure,
            };

            var url = String.format('./format-items/{0}/cluster/{1}/', id, cluster_id);
    
            YAHOO.util.Connect.initHeader('X-CSRFToken', YAHOO.util.Cookie.get('csrftoken'));
            var transaction = YAHOO.util.Connect.asyncRequest('POST', url, callback);
            
            break;
            
        }
    }
    main_dialog.show();
}

function edit_cleanup() {
    main_validation.reset();
	clear_def_table();
}

////////////////////////////////////////////////////////////////////////////////
// delete
////////////////////////////////////////////////////////////////////////////////

function delete_(id) {

    current_delete_id = id;
    
    var records = data_dt.getRecordSet().getRecords();
    for (x=0; x < records.length; x++) {
        var record = records[x];
        var id_record = record.getData('id');
        if(id_record && id == id_record) {
            current_delete_name = record.getData('name').strip();
            break;
        }
    }

    delete_dialog.setBody(String.format('Are you sure you want to delete the SSL/TLS definition [{0}]?', current_delete_name));
    delete_dialog.show();
    
}

// /////////////////////////////////////////////////////////////////////////////

YAHOO.util.Event.onDOMReady(function() {
    setup_main_dialog();
    setup_delete_dialog();
});