
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.RuleEngineAPI = new Class({
    toString: function() {
        var s = '<RuleEngineAPI id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.RuleEngineAPI;
    $.fn.zato.data_table.new_row_func = $.fn.zato.gateway.rule_engine.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'url_path']);

    // Generic connection names are unique per connection type,
    // so the check is scoped to this page's own type.
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name',
            filter_name: 'type_', filter_value: 'gateway-rule-engine'}
    ];
    $.each(unique_constraints, function(index, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name, constraint);
    });

    // Inject the security picker's hidden inputs into the submitted form
    $.fn.zato.data_table.before_submit_hook = function(form) {
        var action = form.attr('id').replace('-form', '');

        form.find('input.badge-member-input[name^="rule_engine_security_"]').remove();
        var sec_assigned = $('#badge-zone-assigned-sec-' + action + ' .badge-zone-body .security-badge');
        sec_assigned.each(function() {
            $.fn.zato.gateway.rule_engine.security_badge_picker_config.inject_hidden_input(form, $(this));
        });

        return true;
    };
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Security badge picker configuration (reuses groups-style badges with sec_type)
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.security_badge_picker_config = {

    make_badge: function(item, num) {
        var badge = $('<div/>', { 'class': 'security-badge', 'data-id': item.id, 'data-security-type': item.sec_type, 'data-name': item.name.toLowerCase() });
        badge.append($('<span/>', { 'class': 'security-badge-indicator' }));
        badge.append($('<span/>', { 'class': 'security-badge-number', 'text': num + '.' }));
        badge.append($('<span/>', { 'class': 'security-badge-type', 'data-security-type': item.sec_type, 'text': item.sec_type_name }));
        badge.append($('<span/>', { 'class': 'security-badge-name', 'text': item.name }));
        return badge;
    },

    sort_items: function(a, b) {
        var type_order = { 'basic_auth': 0, 'apikey': 1 };
        if (type_order[a.sec_type] !== type_order[b.sec_type]) {
            return type_order[a.sec_type] - type_order[b.sec_type];
        }
        return a.name.localeCompare(b.name);
    },

    is_assigned: function(item) {
        return item.is_member;
    },

    filter_badge: function(badge, text_words, type_val) {
        var name = badge.data('name');
        var security_type = badge.data('security-type');

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
            name: 'rule_engine_security_' + member_key,
            value: member_key,
            'class': 'badge-member-input'
        }));
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.security_badge_picker = {};

$.fn.zato.gateway.rule_engine.security_badge_picker.load = function(action, object_id) {
    var sec_action = 'sec-' + action;
    var url = '/zato/rule-engine/api/get-security-list/';
    if (object_id) {
        url += '?object_id=' + object_id;
    }

    var available_body = $('#badge-zone-available-' + sec_action + ' .badge-zone-body');
    available_body.html('<span class="badge-zone-empty">Loading...</span>');

    $.ajax({
        url: url,
        method: 'POST',
        headers: { 'X-CSRFToken': $.cookie('csrftoken') },
        success: function(data) {
            var items = (typeof data === 'string') ? $.parseJSON(data) : data;
            $.fn.zato.badge_picker.init(sec_action, items, $.fn.zato.gateway.rule_engine.security_badge_picker_config);
        },
        error: function(xhr, status, err) {
            available_body.html('<span class="badge-zone-empty">Failed to load</span>');
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.field_descriptions = {
    'id_name': 'A unique name for this object.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this object accepts requests.<br>Callers cannot reach inactive objects.',
    'id_url_path': 'The base URL path rulesets are invoked under,<br>e.g. /api/rules. The ruleset name follows it -<br>POST /api/rules/payments.discounts runs the live<br>version and appending /versions/3 pins one.',
    'id_rulesets': 'Which rulesets this object exposes, comma-separated.<br>A grant is an exact name (payments.discounts),<br>a subtree (payments.*) or everything (*).<br>Names outside the grants answer with 404,<br>the same as names that do not exist,<br>so credentials cannot enumerate what exists.<br>A grant that matches no published ruleset<br>is flagged in the list.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.config = {
    'cluster_id': '1'
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.create = function() {
    $.fn.zato.gateway.rule_engine.security_badge_picker.load('create', null);
    $.fn.zato.data_table._create_edit('create', 'Create a new Rule engine API object', null);
    $('#create-div').dialog('option', 'width', '45em');
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.gateway.rule_engine.field_descriptions
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.edit = function(id) {
    var instance = $.fn.zato.data_table.data[id];
    $.fn.zato.gateway.rule_engine.security_badge_picker.load('edit', instance.id);
    $.fn.zato.data_table._create_edit('edit', 'Update the Rule engine API object', id);
    $('#edit-div').dialog('option', 'width', '45em');
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.gateway.rule_engine.field_descriptions
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// The grants cell: each entry as a chip, flagged when nothing published matches it.
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.grants_html = function(ruleset_grants) {

    if (!ruleset_grants.length) {
        return '<span class="ruleset-grant-none">No grants - nothing can be invoked</span>';
    }

    var out = '';
    for (var grant_idx = 0; grant_idx < ruleset_grants.length; grant_idx++) {
        var grant = ruleset_grants[grant_idx];
        if (grant.is_matched) {
            out += String.format('<span class="ruleset-grant">{0}</span>', grant.name);
        } else {
            out += String.format(
                '<span class="ruleset-grant ruleset-grant-unmatched" title="No published ruleset matches this grant">{0}</span>',
                grant.name);
        }
    }
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;

    // The view always flags the submitted grants the same way the index page does
    var ruleset_grants = data.ruleset_grants;
    var rulesets = data.rulesets;
    var security_count = data.security_count;

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td class="text-center">{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.url_path);
    row += String.format('<td id="rulesets_{0}">{1}</td>', item.id, $.fn.zato.gateway.rule_engine.grants_html(ruleset_grants));
    row += String.format('<td class="text-center" id="security_count_{0}">{1}</td>', item.id, security_count);

    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.gateway.rule_engine.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.gateway.rule_engine.delete_('{0}');\">Delete</a>", item.id));

    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", rulesets);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.gateway.rule_engine.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Rule engine API object `{0}` deleted',
        'Are you sure you want to delete Rule engine API object `{0}`?',
        true);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
