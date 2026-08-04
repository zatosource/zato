

// /////////////////////////////////////////////////////////////////////////////

// What a row of a source with no presenter of its own shows - everything is read
// out of the columns that source already declares, so a new source needs nothing here.

(function($) {

var listing = $.fn.zato.audit_log.listing;

$.fn.zato.audit_log.sources['default'] = {

    // Every column the list does not draw a place of its own for becomes a chip,
    // and each chip is named by its column so clicking it can search by that column's value
    chips: function(row) {
        var columns = $.fn.zato.audit_log.config.columns;
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

    // The message as it went over the wire comes first, and the reading of it,
    // for a payload that carries a document readable as such, comes after.
    detailTabs: function(rowModel) {
        var out = listing.bodyTabs(rowModel);

        out.push(listing.parsedTab());

        return out;
    }
};

// /////////////////////////////////////////////////////////////////////////////

})(jQuery);
