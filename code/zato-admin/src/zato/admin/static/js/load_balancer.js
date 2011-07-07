YAHOO.util.Event.onDOMReady(function() {
    var validate = new YAHOO.widget.Button("validate");
    var validate_save = new YAHOO.widget.Button("validate_save");
    var execute = new YAHOO.widget.Button("execute");

    // Set up the form validation if necessary. Note that the same form ID
    // is used on every page (the forms being different though) so we can simply
    // create the validation object here without worrying if an element with
    // such an ID exists.
    if(typeof lb_manage_validation == "undefined") {
        lb_manage_validation = new Validation("lb-manage", {immediate: true});
    }
});