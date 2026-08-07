

// /////////////////////////////////////////////////////////////////////////////

// What a row of a source with no presenter of its own shows - everything is read
// out of the columns that source already declares, so a new source needs nothing here.

(function($) {

var kit = $.fn.zato.dashboard_kit;
var listing = $.fn.zato.audit_log.listing;

$.fn.zato.audit_log.sources['default'] = {

    // Every column the list does not draw a place of its own for becomes a chip,
    // and each chip is named by its column so clicking it can search by that column's value
    chips: function(row) {
        var audit_log = $.fn.zato.audit_log;
        var columns = audit_log.config.columns;
        var coreColumnKeys = listing.config.coreColumnKeys;
        var out = [];

        for (var columnIndex = 0; columnIndex < columns.length; columnIndex++) {
            var column = columns[columnIndex];

            if (coreColumnKeys[column.key]) {
                continue;
            }

            var value = row[column.key];

            if (value === '') {
                continue;
            }

            // The source wears its human name and no prefix - "REST channel" says
            // what it is without a word before it saying that it says it
            if (column.key === 'source') {
                out.push({key: column.key, label: '', value: value,
                    text: audit_log.sourceLabel(value), tone: 'neutral'});
                continue;
            }

            // The object's name says what it is by itself too, on the page where
            // objects of every source mix on one list
            if (column.key === 'object_name' && audit_log.config.source === '') {
                out.push({key: column.key, label: '', value: value, tone: 'neutral'});
                continue;
            }

            // An endpoint leading with an HTTP method wears the method in its own ink
            if (column.key === 'endpoint') {
                out.push({key: column.key, label: column.label, value: value,
                    value_html: kit.http_method.html(value), tone: 'neutral'});
                continue;
            }

            out.push({key: column.key, label: column.label, value: value, tone: 'neutral'});
        }

        return out;
    },

    // ////////////////////////////////////////////////////////////////////////

    headline: function(row) {
        if (row.msg_id === '') {
            return row.cid;
        }

        return row.msg_id;
    },

    // ////////////////////////////////////////////////////////////////////////

    // What a message of this source is named by and what that name is called -
    // a source with no name of its own for its messages reads by the CID the
    // message travelled under
    identityLabel: 'Message id',

    identity: function(row) {
        if (row.msg_id === '') {
            return row.cid;
        }

        return row.msg_id;
    }
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
