
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// MCP gateway - the controls the gateway list and the wizard share: the two
// badge pickers with their loaders, the PII multi-selects and the master
// toggles enabling the safeguard fields under them.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Services badge picker configuration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.badge_picker_config = {

    make_badge: function(item, num) {
        var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-name': (item.name || '').toLowerCase() });
        badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
        badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
        badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
        return badge;
    },

    sort_items: function(a, b) {
        return (a.name || '').localeCompare(b.name || '');
    },

    is_assigned: function(item) {
        return item.is_member;
    },

    filter_badge: function(badge, text_words, type_val) {
        var name = badge.data('name') || '';
        var text_match = true;

        for (var word_idx = 0; word_idx < text_words.length; word_idx++) {
            if (name.indexOf(text_words[word_idx]) === -1) {
                text_match = false;
                break;
            }
        }

        return text_match;
    },

    inject_hidden_input: function(form, badge) {
        var service_name = badge.data('name');
        form.append($('<input/>', {
            type: 'hidden',
            name: 'mcp_service_' + service_name,
            value: service_name,
            'class': 'badge-member-input'
        }));
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Security badge picker configuration (reuses groups-style badges with sec_type)
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.security_badge_picker_config = {

    make_badge: function(item, num) {
        var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-security-type': item.sec_type, 'data-name': (item.name || '').toLowerCase() });
        badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
        badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
        badge.append($('<span/>', { 'class': 'security-badge-type', 'data-security-type': item.sec_type, 'text': item.sec_type_name || item.sec_type }));
        badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
        return badge;
    },

    sort_items: function(a, b) {
        var type_order = { 'basic_auth': 0, 'apikey': 1 };
        var order_a = type_order[a.sec_type] !== undefined ? type_order[a.sec_type] : 99;
        var order_b = type_order[b.sec_type] !== undefined ? type_order[b.sec_type] : 99;
        if (order_a !== order_b) return order_a - order_b;
        return (a.name || '').localeCompare(b.name || '');
    },

    is_assigned: function(item) {
        return item.is_member;
    },

    filter_badge: function(badge, text_words, type_val) {
        var name = badge.data('name') || '';
        var security_type = badge.data('security-type') || '';

        var type_match = !type_val || security_type === type_val;
        var text_match = true;

        for (var word_idx = 0; word_idx < text_words.length; word_idx++) {
            if (name.indexOf(text_words[word_idx]) === -1) {
                text_match = false;
                break;
            }
        }

        return type_match && text_match;
    },

    inject_hidden_input: function(form, badge) {
        var security_type = badge.data('security-type');
        var security_id = badge.data('id');
        var member_key = security_type + '-' + security_id;
        form.append($('<input/>', {
            type: 'hidden',
            name: 'mcp_security_' + member_key,
            value: member_key,
            'class': 'badge-member-input'
        }));
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Skills badge picker configuration - each badge is one user skill directory
// the gateway serves as an MCP prompt.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.skills_badge_picker_config = {

    make_badge: function(item, num) {
        var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-name': item.name.toLowerCase() });
        badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
        badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
        badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
        return badge;
    },

    sort_items: function(a, b) {
        return a.name.localeCompare(b.name);
    },

    is_assigned: function(item) {
        return item.is_member;
    },

    filter_badge: function(badge, text_words, type_val) {
        var name = badge.data('name');
        var text_match = true;

        for (var word_idx = 0; word_idx < text_words.length; word_idx++) {
            if (name.indexOf(text_words[word_idx]) === -1) {
                text_match = false;
                break;
            }
        }

        return text_match;
    },

    inject_hidden_input: function(form, badge) {
        var skill_name = badge.data('name');
        form.append($('<input/>', {
            type: 'hidden',
            name: 'mcp_skill_' + skill_name,
            value: skill_name,
            'class': 'badge-member-input'
        }));
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.badge_picker = {};
$.fn.zato.gateway.mcp.security_badge_picker = {};
$.fn.zato.gateway.mcp.skills_badge_picker = {};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Brings the service list over and hands it to whoever asked - the wizard fills
// its in-page zones with it, the gateway list builds a whole panel around it
// first, so the panel comes on screen already populated.
$.fn.zato.gateway.mcp.badge_picker.fetch = function(gateway_id, on_items, on_error) {
    var url = '/zato/gateway/mcp/get-service-list/';
    if (gateway_id) {
        url += '?gateway_id=' + gateway_id;
    }

    $.ajax({
        url: url,
        method: 'POST',
        headers: { 'X-CSRFToken': $.cookie('csrftoken') },
        success: function(data) {
            var items = (typeof data === 'string') ? $.parseJSON(data) : data;
            on_items(items);
        },
        error: on_error
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.badge_picker.load = function(action, gateway_id) {

    var available_body = $('#badge-zone-available-' + action + ' .badge-zone-body');
    available_body.html('<span class="badge-zone-empty">Loading...</span>');

    $.fn.zato.gateway.mcp.badge_picker.fetch(gateway_id, function(items) {
        $.fn.zato.badge_picker.init(action, items, $.fn.zato.gateway.mcp.badge_picker_config);
    }, function() {
        available_body.html('<span class="badge-zone-empty">Failed to load</span>');
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.security_badge_picker.fetch = function(gateway_id, on_items, on_error) {
    var url = '/zato/gateway/mcp/get-security-list/';
    if (gateway_id) {
        url += '?gateway_id=' + gateway_id;
    }

    $.ajax({
        url: url,
        method: 'POST',
        headers: { 'X-CSRFToken': $.cookie('csrftoken') },
        success: function(data) {
            var items = (typeof data === 'string') ? $.parseJSON(data) : data;
            on_items(items);
        },
        error: on_error
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.security_badge_picker.load = function(action, gateway_id) {
    var sec_action = 'sec-' + action;

    var available_body = $('#badge-zone-available-' + sec_action + ' .badge-zone-body');
    available_body.html('<span class="badge-zone-empty">Loading...</span>');

    $.fn.zato.gateway.mcp.security_badge_picker.fetch(gateway_id, function(items) {
        $.fn.zato.badge_picker.init(sec_action, items, $.fn.zato.gateway.mcp.security_badge_picker_config);
    }, function() {
        available_body.html('<span class="badge-zone-empty">Failed to load</span>');
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.skills_badge_picker.fetch = function(gateway_id, on_items, on_error) {
    var url = '/zato/gateway/mcp/get-skill-list/';
    if (gateway_id) {
        url += '?gateway_id=' + gateway_id;
    }

    $.ajax({
        url: url,
        method: 'POST',
        headers: { 'X-CSRFToken': $.cookie('csrftoken') },
        success: function(data) {
            var items = (typeof data === 'string') ? $.parseJSON(data) : data;
            on_items(items);
        },
        error: on_error
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.skills_badge_picker.load = function(action, gateway_id) {
    var skills_action = 'skills-' + action;

    var available_body = $('#badge-zone-available-' + skills_action + ' .badge-zone-body');
    available_body.html('<span class="badge-zone-empty">Loading...</span>');

    $.fn.zato.gateway.mcp.skills_badge_picker.fetch(gateway_id, function(items) {
        $.fn.zato.badge_picker.init(skills_action, items, $.fn.zato.gateway.mcp.skills_badge_picker_config);
    }, function() {
        available_body.html('<span class="badge-zone-empty">Failed to load</span>');
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// PII removal - the lands, detectors and exclude fields are Chosen multi-selects.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.pii_select_config = {
    width: '100%',
    include_group_label_in_selected: true,
    search_contains: true,

    // Picking lands or detectors is done in runs of several at a time -
    // the dropdown stays open until it is clicked away or Escape is pressed
    hide_results_on_select: false
};

$.fn.zato.gateway.mcp.pii_select_names = [
    'safeguards_pii_lands',
    'safeguards_pii_detectors',
    'safeguards_pii_exclude'
];

// Chips of this group carry no land prefix - its detector names are global already.
$.fn.zato.gateway.mcp.pii_prefixless_group = 'International';

$.fn.zato.gateway.mcp._format_chip_prefixes = function(select) {

    // The chips live in the Chosen container that follows the underlying select ..
    var chosen = select.data('chosen');
    var container = select.next('.chosen-container');

    container.find('li.search-choice').each(function() {
        var chip = $(this);
        var group_label = chip.find('.group-name');

        if (!group_label.length) {
            return;
        }

        // .. chips of the prefixless group lose their land label entirely ..
        if (group_label.text() === $.fn.zato.gateway.mcp.pii_prefixless_group) {
            group_label.hide();
            return;
        }

        // .. and other chips show the short land code taken from the detector name.
        var option_index = chip.find('.search-choice-close').data('option-array-index');
        var detector_name = chosen.results_data[option_index].value;
        var land_code = detector_name.split('_')[0].toUpperCase();
        group_label.text(land_code);
    });
};

$.fn.zato.gateway.mcp._init_pii_selects = function(action) {

    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    var select_names = $.fn.zato.gateway.mcp.pii_select_names;

    for (var select_idx = 0; select_idx < select_names.length; select_idx++) {

        // Initialize Chosen on the select - a repeated call is a no-op ..
        var select = $('#' + prefix + select_names[select_idx]);
        select.chosen($.fn.zato.gateway.mcp.pii_select_config);

        // .. refresh the badges so a reopened dialog reflects the underlying options ..
        select.trigger('chosen:updated');

        // .. and keep the chip prefixes formatted, now and after every selection.
        select.off('change.pii_prefix').on('change.pii_prefix', function() {
            $.fn.zato.gateway.mcp._format_chip_prefixes($(this));
        });
        $.fn.zato.gateway.mcp._format_chip_prefixes(select);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// URL policy - the allow list wears the same chip look as the PII multi-selects.
// Each host is one chip and the underlying input keeps the whole list as the
// one comma-separated line the endpoints read and write.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.host_list_config = {
    field_name: 'safeguards_url_allow_list',
    separator: ', '
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the underlying input currently holds, one host per entry.
$.fn.zato.gateway.mcp._host_list_values = function(input) {

    var out = [];
    var parts = input.val().split(',');

    for (var part_idx = 0; part_idx < parts.length; part_idx++) {
        var host = parts[part_idx].trim();
        if (host) {
            out.push(host);
        }
    }

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Redraws the chips from the underlying input, keeping the text field last.
$.fn.zato.gateway.mcp._render_host_chips = function(input, choices) {

    choices.find('li.search-choice').remove();

    var hosts = $.fn.zato.gateway.mcp._host_list_values(input);
    var search_field = choices.find('li.search-field');

    for (var host_idx = 0; host_idx < hosts.length; host_idx++) {
        var chip = $('<li/>', {'class': 'search-choice'});
        chip.append($('<span/>', {'text': hosts[host_idx]}));
        chip.append($('<a/>', {'class': 'search-choice-close', 'data-host': hosts[host_idx]}));
        chip.insertBefore(search_field);
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp._init_host_list = function(action) {

    var config = $.fn.zato.gateway.mcp.host_list_config;

    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    var input = $('#' + prefix + config.field_name);

    // The widget is built once for the page's lifetime
    if (input.data('host-list-built')) {
        return;
    }
    input.data('host-list-built', true);

    // The same container and list classes the Chosen multi-selects render with,
    // so the stylesheet the detectors wear dresses the chips here too ..
    var container = $('<div/>', {'class': 'chosen-container chosen-container-multi mcp-host-list'});
    var choices = $('<ul/>', {'class': 'chosen-choices'});
    var search_field = $('<li/>', {'class': 'search-field'});
    // The autocomplete attribute goes through attr - in the creation map,
    // jQuery would call the UI plugin of the same name instead of setting it
    var text_field = $('<input/>', {type: 'text', placeholder: input.attr('placeholder')});
    text_field.attr('autocomplete', 'off');

    search_field.append(text_field);
    choices.append(search_field);
    container.append(choices);

    // .. the widget stands in for the input, which keeps the value out of sight ..
    input.hide();
    container.insertAfter(input);

    var render = function() {
        $.fn.zato.gateway.mcp._render_host_chips(input, choices);
    };

    // .. whatever was typed becomes chips - commas split a pasted list -
    // and the input hears about every change the way any field would ..
    var commit_text = function() {

        var hosts = $.fn.zato.gateway.mcp._host_list_values(input);
        var parts = text_field.val().split(',');
        var added = false;

        for (var part_idx = 0; part_idx < parts.length; part_idx++) {
            var host = parts[part_idx].trim();
            if (host) {
                if (hosts.indexOf(host) === -1) {
                    hosts.push(host);
                    added = true;
                }
            }
        }

        text_field.val('');

        if (added) {
            input.val(hosts.join(config.separator));
            render();
            input.trigger('change');
        }
    };

    var remove_host = function(host) {

        var hosts = $.fn.zato.gateway.mcp._host_list_values(input);
        var host_idx = hosts.indexOf(host);

        hosts.splice(host_idx, 1);
        input.val(hosts.join(config.separator));
        render();
        input.trigger('change');
    };

    // .. Enter and comma add what was typed - the event stops here so the
    // form-wide Enter handling stays out of it - and Backspace in an empty
    // field takes the last chip back ..
    text_field.on('keydown', function(event) {

        if (event.key === 'Enter' || event.key === ',') {
            event.preventDefault();
            event.stopPropagation();
            commit_text();
            return;
        }

        if (event.key === 'Backspace') {
            if (!text_field.val()) {
                var hosts = $.fn.zato.gateway.mcp._host_list_values(input);
                if (hosts.length) {
                    event.preventDefault();
                    remove_host(hosts[hosts.length - 1]);
                }
            }
        }
    });

    // .. leaving the field commits what was typed, so nothing is lost
    // to a click on Next or Save ..
    text_field.on('focus', function() {
        container.addClass('chosen-container-active');
    });

    text_field.on('blur', function() {
        container.removeClass('chosen-container-active');
        commit_text();
    });

    // .. a chip's close mark removes it, a click anywhere else invites typing ..
    choices.on('click', '.search-choice-close', function() {
        remove_host($(this).data('host'));
    });

    choices.on('click', function(event) {
        if (event.target === this) {
            text_field.trigger('focus');
        }
    });

    // .. the container follows the disabled state of the input it wraps,
    // told about it the way the Chosen selects are ..
    var sync_disabled = function() {
        var is_disabled = input.prop('disabled');
        container.toggleClass('chosen-disabled', is_disabled);
        text_field.prop('disabled', is_disabled);
    };

    input.on('host-list:updated', sync_disabled);
    sync_disabled();

    // .. and the chips open on whatever the input arrived with.
    render();
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Master toggles in the response safeguards fields - each key is a checkbox that
// enables or disables the inputs listed under it.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp.safeguard_groups = {
    'safeguards_pii_enabled': [
        'safeguards_pii_lands',
        'safeguards_pii_detectors',
        'safeguards_pii_exclude',
        'safeguards_pii_validate',
        'safeguards_pii_stable_replacements'
    ],
    'safeguards_normalize_unicode': [
        'safeguards_unicode_mode'
    ],
    'safeguards_sanitize_markup': [
        'safeguards_markup_mode'
    ],
    'safeguards_url_policy_enabled': [
        'safeguards_url_allow_list',
        'safeguards_url_mode'
    ]
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.mcp._init_safeguard_toggles = function(action) {

    var prefix = action === 'edit' ? 'id_edit-' : 'id_';
    var groups = $.fn.zato.gateway.mcp.safeguard_groups;

    $.each(groups, function(master_name, dependent_names) {

        var master = $('#' + prefix + master_name);

        // Enable or disable every dependent input based on the master checkbox ..
        var apply_state = function() {
            var is_enabled = master.is(':checked');
            $.each(dependent_names, function(dependent_idx, dependent_name) {
                var dependent = $('#' + prefix + dependent_name);
                dependent.prop('disabled', !is_enabled);
                dependent.toggleClass('routing-disabled', !is_enabled);

                // Chosen mirrors the disabled state only when told the select changed
                if (dependent.hasClass('chosen-multi')) {
                    dependent.trigger('chosen:updated');
                }

                // The host list widget mirrors it the same way
                if (dependent.data('host-list-built')) {
                    dependent.trigger('host-list:updated');
                }
            });
        };

        // .. re-apply on every change and once now for the initial state.
        master.off('change.safeguards').on('change.safeguards', apply_state);
        apply_state();
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
