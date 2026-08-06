

/* Dashboard kit - the attachment strip.
   The files one record carries, a badge to a file - its name and its size, clicked to download.
   A file whose bytes were over the audit cap is named but leads nowhere, saying so instead.
   The strip only appears at all once the record is known to carry anything, so its metadata
   is asked for when the record is opened and a record with no attachments shows nothing. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.attachments = {};

    kit.attachments.config = {
        label: 'Attachments',

        // What a file whose bytes were not kept says instead of a download
        not_kept_label: 'not kept',

        // The units a size is read in, each one a thousand of the one before it
        size_units: ['B', 'KB', 'MB', 'GB'],
        size_unit_step: 1000,

        // The badge each variant wears, the same two the fact rows wear
        badge_classes: {
            'light': 'dashboard-panel-action-badge-light',
            'dark': 'dashboard-panel-action-badge-dark'
        }
    };

    /* A size in bytes as a person reads it - the largest unit it still has a whole part in. */
    kit.attachments.format_size = function(size) {
        var config = kit.attachments.config;
        var units = config.size_units;

        var unit_index = 0;
        var value = size;

        while (value >= config.size_unit_step && unit_index < units.length - 1) {
            value = value / config.size_unit_step;
            unit_index += 1;
        }

        // Whole bytes are exact and everything above them is read to one decimal place
        if (unit_index === 0) {
            return value + ' ' + units[unit_index];
        }

        return value.toFixed(1) + ' ' + units[unit_index];
    };

    /* One attachment as one badge - a download for a file whose bytes were kept,
       and only its name and the reason there is nothing to download otherwise. */
    kit.attachments.badge_html = function(item, download_url, variant) {
        var config = kit.attachments.config;
        var badge_class = 'dashboard-panel-action-badge ' + config.badge_classes[variant] +
            ' dashboard-attachment-badge';

        var text = kit._esc_html(item.filename) +
            ' <span class="dashboard-attachment-size">' +
            kit.attachments.format_size(item.size) + '</span>';

        if (!item.is_content_kept) {
            return '<span class="' + badge_class + ' dashboard-attachment-not-kept">' + text +
                ' \u00b7 ' + config.not_kept_label + '</span>';
        }

        var href = download_url + '?id=' + item.id;

        var out = '<a class="' + badge_class + '" href="' + kit._esc_html(href) + '">' + text + '</a>';

        return out;
    };

    /* The whole strip - its label and one badge per file. `variant` is 'light' or 'dark'. */
    kit.attachments.strip_html = function(items, download_url, variant) {
        var config = kit.attachments.config;

        var out = '<div class="dashboard-attachments">';
        out += '<span class="dashboard-attachments-label">' + config.label + '</span>';

        for (var item_index = 0; item_index < items.length; item_index++) {
            out += kit.attachments.badge_html(items[item_index], download_url, variant);
        }

        out += '</div>';

        return out;
    };

    /* Asks for one record's attachments and puts the strip where the caller points, or nothing
       at all when the record carries none. `options` names the two endpoints, the record and
       the variant - list_url, download_url, id, variant. */
    kit.attachments.load = function($host, options) {
        $.ajax({
            url: options.list_url,
            type: 'POST',
            data: JSON.stringify({id: options.id}),
            contentType: 'application/json',
            headers: {'X-CSRFToken': $.cookie('csrftoken')},
            success: function(data) {
                if (typeof data === 'string') {
                    data = JSON.parse(data);
                }

                // A record moved away from while its files were on their way says nothing
                // about them on whatever the host is holding now
                if (String($host.attr('data-attachments-id')) !== String(options.id)) {
                    return;
                }

                if (data.attachments.length === 0) {
                    $host.empty();
                    return;
                }

                $host.html(kit.attachments.strip_html(
                    data.attachments, options.download_url, options.variant));
            }
        });
    };
})();
