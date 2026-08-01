
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
