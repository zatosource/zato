
YAHOO.util.Event.onDOMReady(function() {

    var update_definition_submit = new YAHOO.widget.Button("update_definition_submit");

    // Set up the form validation if necessary.
    if(typeof edit_validation == "undefined") {
        edit_validation = new Validation("update_definition_form", {immediate: true});
    }
    edit_validation.reset();

    YAHOO.namespace("zato.progress_bar");

    function init() {

        if(!edit_validation.validate()) {
            return;
        }

        var content = document.getElementById("content");

        content.innerHTML = "";

        if (!YAHOO.zato.progress_bar.wait) {

            // Initialize the temporary Panel to display while waiting for external content to load

            YAHOO.zato.progress_bar.wait =
                    new YAHOO.widget.Overlay("wait",
                                                    { width: "240px",
                                                      fixedcenter: true,
                                                      close: false,
                                                      draggable: false,
                                                      zindex:4,
                                                      modal: true,
                                                      visible: false
                                                    }
                                                );

            YAHOO.zato.progress_bar.wait.setHeader("Please wait");
            YAHOO.zato.progress_bar.wait.setBody("<img src=\"/static/gfx/ajax-loader.gif\"/>");
            YAHOO.zato.progress_bar.wait.render(document.body);

        }

        var callback = {
            success : function(o) {
                update_user_message(true, "Succesfully saved the changes");
                YAHOO.zato.progress_bar.wait.hide();
            },
            failure : function(o) {
                update_user_message(false, o.responseText);
                YAHOO.zato.progress_bar.wait.hide();
            }
        }

        // Show the Panel
        YAHOO.zato.progress_bar.wait.show();

        YAHOO.util.Connect.setForm(document.getElementById("update_definition_form"));
        var conn = YAHOO.util.Connect.asyncRequest("POST", "./edit/", callback);
    }

    YAHOO.util.Event.on("update_definition_submit", "click", init);
});