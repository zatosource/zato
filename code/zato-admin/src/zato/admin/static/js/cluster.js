
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.Cluster = new Class({
	toString: function() {
		var s = '<Cluster id:{0} name:{1}>';
		return String.format(s, this.id ? this.id : '(none)', 
								this.name ? this.name : '(none)');
	}
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() { 
	$('#data-table').tablesorter(); 
	$.fn.zato.data_table.class_ = $.fn.zato.data_table.Cluster;
	$.fn.zato.data_table.new_row_func = $.fn.zato.cluster.data_table.new_row;
	$.fn.zato.data_table.parse();
	var attrs = ['name', 'odb_host', 'odb_port', 'odb_db_name', 'odb_user', 
		'lb_host', 'lb_agent_port', 'broker_host', 'broker_start_port', 'broker_token'];
	$.fn.zato.data_table.setup_forms(attrs);
})

$.fn.zato.cluster.create = function() {
	$.fn.zato.data_table._create_edit('create', 'Create a new cluster', null);
}

$.fn.zato.cluster.edit = function(id) {
	$.fn.zato.data_table._create_edit('edit', "Update the cluster's definition", id);
}


$.fn.zato.cluster.data_table.new_row = function(item, data, include_tr) {
    var row = '';
	
	if(include_tr) {
		row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
	}
	
	row += "<td class='numbering'>&nbsp;</td>";
	row += "<td><input type='checkbox' /></td>";
	row += String.format('<td>{0}</td>', item.name);
	row += String.format('<td>{0}</td>', '');//item.is_active ? 'Yes' : 'No');
	row += String.format('<td>{0}</td>', '');//item.username);
	row += String.format('<td>{0}</td>', '');//item.domain);
	row += String.format('<td>{0}</td>', '');//String.format("<a href='javascript:$.fn.zato.cluster.edit({0})'>Edit</a>", item.id));
	row += String.format('<td>{0}</td>', String.format("<a href='javascript:$.fn.zato.cluster.delete_({0});'>Delete</a>", item.id));
	row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
	row += String.format("<td class='ignore'>{0}</td>", '');
	
	if(include_tr) {
		row += '</tr>';
	}
	
	return row;
}

$.fn.zato.security.basic_auth.delete_ = function(id) {
	$.fn.zato.data_table.delete_(id, 'td.item_id_', 
		'HTTP Basic Auth definition [{0}] deleted', 
		'Are you sure you want to delete the HTTP Basic Auth definition [{0}]?');
}


/*

// A base class for representing a cluster
var Cluster = Class.create({
    initialize: function() {
        this.cluster_id = null;
        this.name = null;
        this.description = null;
        this.servers = null;
        this.addresses = null;

    }
});

// A nicer toString.
Cluster.prototype.toString = function() {
    return "<Cluster\
 name=[" + this.name + "]\
 servers=[" + this.servers + "]\
 addresses=[" + this.addresses + "]\
>";
};

Cluster.prototype.name_html = function() {
    return "<a href=\"javascript:cluster_manage('"+ this.cluster_id +"')\">"+ this.name +"</a>";
}

Cluster.prototype.description_html = function() {
    if(this.description) {
        return "<br/><span style=\"font-size:80%\"><pre>" + this.description +
            "</pre></span>";
    }
    return "";
}

Cluster.prototype.update_record_addresses = function(data_dt, record) {

    var on_get_addresses_success = function(o) {

        var get_address = function(scheme, address, port, path) {
            var url = scheme + "://" + address + ":" + port;
            if(path) {
                url += path;
            }
            return "<a href=\"" + url + "\">" + url + "</a>";
        }

        var json = YAHOO.lang.JSON.parse(o.responseText);

        var addresses_html = "<span style=\"font-size:90%\">";
        var lb_agent_html = "LB agent: ";
        var front_http_plain_html = "Plain HTTP: ";
        var front_https_no_certs_html = "SSL without client certs: ";
        var front_https_certs_html = "SSL with client certs: ";
        var monitor_uri_html = "LB health-check: ";

        if(json.cluster) {
            var lb_agent_url = "https://" + json.cluster.lb_host + ":" + json.cluster.lb_agent_port + "/RPC2";
            lb_agent_html += "<a href=\"" + lb_agent_url + "\">" + lb_agent_url + "</a>";
        }
        else {
            lb_agent_html += "Could not fetch config";
        }

        if(json.cluster.lb_config) {
            front_http_plain_html += get_address("http",
                json.cluster.lb_config.frontend.front_http_plain.bind.address,
                json.cluster.lb_config.frontend.front_http_plain.bind.port,
                "");

            front_https_no_certs_html += get_address("https",
                json.cluster.lb_config.frontend.front_https_no_certs.bind.address,
                json.cluster.lb_config.frontend.front_https_no_certs.bind.port,
                "");

            front_https_certs_html += get_address("https",
                json.cluster.lb_config.frontend.front_https_certs.bind.address,
                json.cluster.lb_config.frontend.front_https_certs.bind.port,
                "");

            monitor_uri_html += get_address("http",
                json.cluster.lb_config.frontend.front_http_plain.bind.address,
                json.cluster.lb_config.frontend.front_http_plain.bind.port,
                json.cluster.lb_config.frontend.front_http_plain.monitor_uri);
        }
        else {
            front_http_plain_html += "Could not fetch config";
            front_https_no_certs_html += "Could not fetch config";
            front_https_certs_html += "Could not fetch config";
            monitor_uri_html += "Could not fetch config";
        }

        addresses_html += lb_agent_html;
        addresses_html += "<br/>" + front_http_plain_html;
        addresses_html += "<br/>" + front_https_no_certs_html;
        addresses_html += "<br/>" + front_https_certs_html;
        addresses_html += "<br/>" + monitor_uri_html;
        addresses_html += "</span>";

        data_dt.updateCell(record, "addresses", addresses_html);
    }

    var on_get_addresses_failure = function(o) {
        update_user_message(false, o.responseText);
    }

    var callback = {
        success: on_get_addresses_success,
        failure: on_get_addresses_failure,
    };

    YAHOO.util.Connect.asyncRequest("GET", "/zato/load-balancer/get-addresses/cluster/" + this.cluster_id, callback);
}
Cluster.prototype.update_edit_manage_links = function(data_dt, record) {
    var html = "";
    html += "<a href=\"javascript:cluster_edit('"+ this.cluster_id +"')\">Edit cluster</a>";
    html += "<br/>";
    html += "<a href=\"/zato/load-balancer/manage/cluster/"+ this.cluster_id +"\">Manage load-balancer</a>";
    html += "<br/>";
    html += "<a href=\"javascript:cluster_delete('"+ this.cluster_id +"')\">Delete cluster</a>";

    data_dt.updateCell(record, "edit_manage", html);
}

// Dumps properties in a form suitable for creating a new data table row.
Cluster.prototype.to_record = function() {
    var record = new Array();
    record["cluster"] = this.name_html() + this.description_html();

    return record;
};

Cluster.prototype.add_row = function(cluster, data_dt) {

    this.name = $("id_name").value;

    var on_get_success = function(o) {
        var json = YAHOO.lang.JSON.parse(o.responseText)[0];
        cluster.cluster_id = json.pk;
        cluster.description = json.fields.description;

        var add_at_idx = 0;

        // We're adding the record now but the actual HTML-formatted values
        // will be overridden in 'on_get_server_state_success provided that
        // load-balancer answers.
        data_dt.addRow(cluster.to_record(), add_at_idx);

        var added_record = data_dt.getRecord(add_at_idx)
        added_record.setData("cluster_id", cluster.cluster_id);

        var on_get_server_state_success = function(o) {

            var cluster = o.argument[0];
            var data_dt = o.argument[1];
            var record = o.argument[2];
            var cluster_id = o.argument[3];
            var cluster_name = o.argument[4];
            var cluster_description = o.argument[5];

            cluster.cluster_id = cluster_id;

            // o.responseText contains the HTML-formatted information
            // about the state of servers.
            cluster.name = cluster_name + o.responseText;

            cluster.description = cluster_description;
            record.setData("cluster", cluster.name_html() + cluster.description_html());
            cluster.update_record_addresses(data_dt, record);

            data_dt.render();
        }

        var on_get_server_state_failure = function(o) {
            // The load-balancer couldn't be contacted however it doesn't mean
            // we weren't able to add the cluster itself.
            update_user_message(false, "Warning: cluster has been created succesfully however the load-balancer's agent could not be contacted");
        }

        var callback = {
            success: on_get_server_state_success,
            failure: on_get_server_state_failure,
            argument: [cluster, data_dt, added_record, cluster.cluster_id,
                        cluster.name, cluster.description]
        };

        YAHOO.util.Connect.asyncRequest("GET", "./servers-state/" + cluster.cluster_id, callback);

        cluster.update_record_addresses(data_dt, added_record);
        cluster.update_edit_manage_links(data_dt, added_record);
    }

    var on_get_failure = function(o) {
        update_user_message(false, o.responseText);
    }

    var callback = {
        success: on_get_success,
        failure: on_get_failure,
    };

    YAHOO.util.Connect.asyncRequest("GET", "/zato/cluster/get/by-name/" + this.name + "/", callback);
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

        var cluster = new Cluster();
        cluster.add_row(cluster, data_dt);

        // Hide the dialog and confirm the changes have been saved.
        create_dialog.hide();

        update_user_message(true, "Succesfully created a new cluster");

        // Cleanup after work.
        create_cleanup();

    };

    var on_create_failure = function(o) {
        create_cleanup();
        update_user_message(false, o.responseText);
        create_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("create-cluster", "yui-pe-content");

    // Instantiate the dialog.
    create_dialog = new YAHOO.widget.Dialog("create-cluster",
                            { width: "69em",
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

function cluster_create() {

    // Set up the form validation if necessary.
    if(typeof create_validation == "undefined") {
        create_validation = new Validation("create-form");
    }
    create_validation.reset();
    create_dialog.show();
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

        var cluster = new Cluster();

        edit_dialog.hide();

        var records = data_dt.getRecordSet().getRecords();
        for (x=0; x < records.length; x++) {
            var record = records[x];
            var cluster_id = record.getData("cluster_id");

            if(cluster_id && cluster_id ==  $("id_edit-cluster_id").value) {

                var on_get_server_state_success = function(o) {

                    var cluster = o.argument[0];
                    var data_dt = o.argument[1];
                    var record = o.argument[2];
                    var cluster_id = o.argument[3];
                    var cluster_name = o.argument[4];
                    var cluster_description = o.argument[5];

                    cluster.cluster_id = cluster_id;

                    // o.responseText contains the HTML-formatted information
                    // about the state of servers.
                    cluster.name = cluster_name + o.responseText;

                    cluster.description = cluster_description;
                    record.setData("cluster", cluster.name_html() + cluster.description_html());
                    cluster.update_record_addresses(data_dt, record);

                    data_dt.render();
                    edit_cleanup();

                    update_user_message(true, "Succesfully saved changes");
                }

                var on_get_server_state_failure = function(o) {
                    update_user_message(false, "Caught an exception=[" + o.responseText + "]");
                }

                var callback = {
                    success: on_get_server_state_success,
                    failure: on_get_server_state_failure,
                    argument: [cluster, data_dt, record, cluster_id,
                                $("id_edit-name").value,
                                $("id_edit-description").value]
                };

                YAHOO.util.Connect.asyncRequest("GET", "./servers-state/" + cluster_id, callback);

            }
        }
    };

    var on_edit_failure = function(o) {
        edit_cleanup();
        update_user_message(false, o.responseText);
        edit_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("edit-cluster", "yui-pe-content");

    // Instantiate the dialog.
    edit_dialog = new YAHOO.widget.Dialog("edit-cluster",
                            { width: "69em",
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

function cluster_edit(cluster_id) {

    // Set up the form validation if necessary.
    if(typeof edit_validation == "undefined") {
        edit_validation = new Validation("edit-form");
    }
    edit_cleanup();

    // Get the cluster's details from DB.

    var on_get_cluster_success = function(o) {
        var json = YAHOO.lang.JSON.parse(o.responseText);
        var cluster = json[0].fields;

        $("id_edit-cluster_id").value = json[0].pk;
        $("id_edit-name").value = cluster.name;
        $("id_edit-description").value = cluster.description;
        $("id_edit-odb_engine").value = cluster.odb_engine;
        $("id_edit-odb_host").value = cluster.odb_host;
        $("id_edit-odb_port").value = cluster.odb_port;
        $("id_edit-odb_user").value = cluster.odb_user;
        $("id_edit-odb_db_name").value = cluster.odb_db_name;
        $("id_edit-odb_schema").value = cluster.odb_schema;
        $("id_edit-amqp_host").value = cluster.amqp_host;
        $("id_edit-amqp_port").value = cluster.amqp_port;
        $("id_edit-amqp_user").value = cluster.amqp_user;
        $("id_edit-lb_host").value = cluster.lb_host;
        $("id_edit-lb_agent_port").value = cluster.lb_agent_port;

        edit_dialog.show();
    };

    var on_get_cluster_failure = function(o) {
        update_user_message(false, o.responseText);
    }

    var callback = {
        success: on_get_cluster_success,
        failure: on_get_cluster_failure,
    };

    YAHOO.util.Connect.asyncRequest("GET", "./get/by-id/" + cluster_id, callback);
}

////////////////////////////////////////////////////////////////////////////////
// delete
////////////////////////////////////////////////////////////////////////////////
function delete_cleanup() {
    delete_validation.reset();
    $("delete-form").reset();
}

function setup_delete_dialog() {

    var on_delete_submit = function() {
        if(delete_validation.validate()) {
            var answer = $("id_delete-answer").value;
            if(answer == "YES") {
                this.submit();
                delete_validation.reset();
            }
        }
    };

    var on_delete_cancel = function() {
        this.cancel();
        delete_cleanup();
    };

    var on_delete_success = function(o) {

        var cluster = new Cluster();

        delete_dialog.hide();

        var records = data_dt.getRecordSet().getRecords();
        for (x=0; x < records.length; x++) {
            var record = records[x];
            var cluster_id = record.getData("cluster_id");

            if(cluster_id && cluster_id ==  $("id_delete-cluster_id").value) {
                data_dt.deleteRow(record);
                update_user_message(true, "Cluster deleted succesfully");
            }
        }
    };

    var on_delete_failure = function(o) {
        delete_cleanup();
        update_user_message(false, o.responseText);
        delete_dialog.hide();
    };

    // Remove progressively enhanced content class, just before creating the module.
    YAHOO.util.Dom.removeClass("delete-cluster", "yui-pe-content");

    // Instantiate the dialog.
    delete_dialog = new YAHOO.widget.Dialog("delete-cluster",
                            { width: "50em",
                              fixedcenter: true,
                              visible: false,
                              draggable: true,
                              postmethod: "async",
                              hideaftersubmit: false,
                              constraintoviewport: true,
                              buttons: [{text:"Submit", handler:on_delete_submit},
                                        {text:"Cancel", handler:on_delete_cancel, isDefault:true}]
                            });

    delete_dialog.callback.success = on_delete_success;
    delete_dialog.callback.failure = on_delete_failure;

    // Render the dialog.
    delete_dialog.render();
}

function cluster_delete(cluster_id) {

    // Set up the form validation if necessary.
    if(typeof delete_validation == "undefined") {
        delete_validation = new Validation("delete-form");
    }
    delete_cleanup();

    // Get cluster's details from DB.

    var on_get_cluster_success = function(o) {
        var json = YAHOO.lang.JSON.parse(o.responseText);
        var cluster = json[0].fields;

        $("delete-name").innerHTML = cluster.name;
        $("id_delete-cluster_id").value = json[0].pk;

        delete_dialog.show();
    };

    var on_get_cluster_failure = function(o) {
        update_user_message(false, o.responseText);
    }

    var callback = {
        success: on_get_cluster_success,
        failure: on_get_cluster_failure,
    };

    YAHOO.util.Connect.asyncRequest("GET", "./get/by-id/" + cluster_id, callback);
}

YAHOO.util.Event.onDOMReady(function() {
    setup_create_dialog();
    setup_edit_dialog();
    setup_delete_dialog();
});

*/