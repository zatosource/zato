
// HL7 MLLP outgoing connections - the list page.
//
// Creating and editing a connection happen in the wizard, on a page of its
// own, so this file only holds what the table itself needs. The per-field
// help texts the wizard also uses live in mllp-descriptions.js.

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HL7MLLPOutconn = new Class({
    toString: function() {
        var s = '<HL7MLLPOutconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HL7MLLPOutconn;
    $.fn.zato.data_table.parse();
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HL7 MLLP outgoing connection `{0}` deleted',
        'Are you sure you want to delete HL7 MLLP outgoing connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp._default_hl7_message = ''
    + 'MSH|^~\\&|WELLNESS_APP|MAIN_FAC|SCHEDULING|MAIN_FAC|20240315120000||ADT^A04^ADT_A01|MSG00001|P|2.9\r'
    + 'EVN|A04|20240315120000\r'
    + 'PID|1||12345^^^FAC^MR||SMITH^JOHN^A||19800115|M\r'
    + 'PV1|1|O\r';

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.get_invoke_url = function(id) {
    var item = $.fn.zato.data_table.data[id];
    return '/zato/outgoing/hl7/mllp/invoke/action/' + encodeURIComponent(item.name) + '/';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.hl7.mllp.invoke = function(id) {
    var item = $.fn.zato.data_table.data[id];

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        history_key: 'zato.invoke-history.outgoing-hl7-mllp.' + id,
        get_invoke_url_func: $.fn.zato.outgoing.hl7.mllp.get_invoke_url,
        show_more_options: false,
        title_prefix: 'Invoke HL7 MLLP connection',
        default_request: $.fn.zato.outgoing.hl7.mllp._default_hl7_message,
    });

    $.fn.zato.invoker._request_ace_mode = 'ace/mode/hl7';

    // The pane exists only from the second opening onwards, the first one reads the mode set above
    var pane = $.fn.zato.invoker._request_pane;
    if (pane) {
        pane.getEditor().session.setMode('ace/mode/hl7');
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
