
var ping_server_response_success = function(o) {
    var server_id = o.argument;
    var elem = YAHOO.util.Dom.get("ping_server_" + server_id);
    elem.innerHTML = o.responseText;
};

var ping_server_response_failure = function(o) {
    // TODO: Proper handling of failures
    alert(o.responseText);
};

function ping_server(server_id) {

    var callback = {
      success: ping_server_response_success,
      failure: ping_server_response_failure,
      argument: server_id
    };

    var transaction = YAHOO.util.Connect.asyncRequest("GET", "/zato/servers/ping/" + server_id, callback, null);
};

YAHOO.util.Event.onDOMReady(function() {

    var on_submit = function() {
        this.submit();
    };
    var on_cancel = function() {
        this.cancel();
    };

    // Remove progressively enhanced content class, just before creating the module
    YAHOO.util.Dom.removeClass("edit-server", "yui-pe-content");

    // Instantiate the Dialog
    edit_server_dialog = new YAHOO.widget.Dialog("edit-server",
                            { width: "30em",
                              fixedcenter: true,
                              visible: false,
                              draggable: true,
                              postmethod: "form",
                              hideaftersubmit: true,
                              constraintoviewport: true,
                              buttons: [{text:"Submit", handler:on_submit},
                                        {text:"Cancel", handler:on_cancel, isDefault:true}]
                            });

    // Render the Dialog
    edit_server_dialog.render();
});

function edit_server(server_id, name, address) {
    YAHOO.util.Dom.get("id_edit-server_id").value = server_id;
    YAHOO.util.Dom.get("id_edit-name").value = name;
    YAHOO.util.Dom.get("id_edit-address").value = address;
    edit_server_dialog.show();
}
