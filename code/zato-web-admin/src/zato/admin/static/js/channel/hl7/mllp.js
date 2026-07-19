
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HL7MLLPChannel = new Class({
    toString: function() {
        var s = '<HL7MLLPChannel id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HL7MLLPChannel;
    $.fn.zato.data_table.parse();
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HL7 MLLP channel `{0}` deleted',
        'Are you sure you want to delete HL7 MLLP channel `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.config = {
    cluster_id: '1',
    import_demo_url: '/zato/channel/hl7/mllp/import-demo-config'
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.import_demo_config = function() {
    var config = $.fn.zato.channel.hl7.mllp.config;
    var import_url = config.import_demo_url + '?cluster=' + config.cluster_id;

    var spinner_html = '<div id="import-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 9999;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Importing ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $('body').append(spinner_html);

    $.ajax({
        url: import_url,
        method: 'GET',
        success: function() {
            $('#import-spinner').remove();
            window.location.reload();
        },
        error: function() {
            $('#import-spinner').remove();
            alert('Import failed. Check server logs.');
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp._default_hl7_message = ''
    + 'MSH|^~\\&|WELLNESS_APP|MAIN_FAC|SCHEDULING|MAIN_FAC|20240315120000||ADT^A04^ADT_A01|MSG00001|P|2.9\r'
    + 'EVN|A04|20240315120000\r'
    + 'PID|1||12345^^^FAC^MR||SMITH^JOHN^A||19800115|M\r'
    + 'PV1|1|O\r';

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.get_invoke_url = function(id) {
    return '/zato/channel/hl7/mllp/invoke/' + id + '/';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.invoke = function(id) {
    var item = $.fn.zato.data_table.data[id];

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        history_key: 'zato.invoke-history.channel-hl7-mllp.' + id,
        get_invoke_url_func: $.fn.zato.channel.hl7.mllp.get_invoke_url,
        show_more_options: false,
        title_prefix: 'Invoke HL7 MLLP channel',
        default_request: $.fn.zato.channel.hl7.mllp._default_hl7_message,
    });

    $.fn.zato.invoker._request_ace_mode = 'ace/mode/hl7';

    var pane = $.fn.zato.invoker._request_pane;
    if (pane) {
        pane.getEditor().session.setMode('ace/mode/hl7');
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
