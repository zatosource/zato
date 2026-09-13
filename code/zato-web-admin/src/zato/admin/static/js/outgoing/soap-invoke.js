
// ////////////////////////////////////////////////////////////////////////////
// Outgoing SOAP connections - the Invoke dialog
// ////////////////////////////////////////////////////////////////////////////

// The dialog sends an operation and the XML of the operation's message through a connection, where the REST
// one sends a method and a payload - the same overlay, with an Operation field in place of the HTTP options.

(function($) {

    $.fn.zato.outgoing.soap.invoke_config = {

        // Where the dialog posts to - the one outgoing invoke endpoint, which reads the connection's transport
        invokeUrlPrefix: '/zato/http-soap/invoke-outconn/',

        // What the history of one connection's invocations is stored under
        historyKeyPrefix: 'zato.invoke-history.outconn-soap.',

        // The body is XML, as is the response
        highlightLexer: 'xml',
        aceMode: 'ace/mode/xml',

        // What the body looks like before the first invocation - the operation element with one child
        defaultRequest: '<Request>\n  <id>1</id>\n</Request>',

        // The field the operation is typed into
        operationFieldId: 'invoker-modal-operation',
        operationPlaceholder: 'e.g. GetOrder - empty means the connection\'s own'
    };

    var config = $.fn.zato.outgoing.soap.invoke_config;

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.get_invoke_url = function(id) {
        var out = config.invokeUrlPrefix + id + '/';
        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.collect_invoke_form_data = function() {
        var request = $.fn.zato.invoker._request_pane.getValue();
        var operation = $('#' + config.operationFieldId).val();

        var out = {
            'data-request': request,
            'operation': operation
        };

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    $.fn.zato.outgoing.soap.invoke = function(id) {
        var item = $.fn.zato.data_table.data[id];
        if (!item) {
            return;
        }

        var historyKey = config.historyKeyPrefix + id;

        $.fn.zato.invoker.open_overlay({
            id: id,
            name: item.name,
            connection: 'outconn-soap',
            history_key: historyKey,
            highlight_lexer: config.highlightLexer,
            default_request: config.defaultRequest,
            show_more_options: false,
            extra_fields_html: '<div class="invoker-more-options-row invoker-more-options-row-compact">'
                + '<label>Operation</label>'
                + '<input type="text" id="' + config.operationFieldId + '" placeholder="' + config.operationPlaceholder + '" />'
                + '</div>',
            get_invoke_url_func: $.fn.zato.outgoing.soap.get_invoke_url,
            collect_form_data_func: $.fn.zato.outgoing.soap.collect_invoke_form_data
        });

        // The body is XML, so the pane that was just mounted is switched over to it
        $.fn.zato.invoker._request_ace_mode = config.aceMode;

        var editor = $.fn.zato.invoker._request_pane.getEditor();
        editor.session.setMode(config.aceMode);
    };

    // ////////////////////////////////////////////////////////////////////////

})(jQuery);
