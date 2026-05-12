
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.GraphQLOutconn = new Class({
    toString: function() {
        var s = '<GraphQLOutconn id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.GraphQLOutconn;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.graphql.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms([
        'name',
        'address',
        'default_query_timeout',
        'security_id',
    ]);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.field_descriptions = {
    'id_name': 'A unique name for this GraphQL connection.<br>Used to identify it in logs and the dashboard.',
    'id_is_active': 'Whether this connection is active.<br>Inactive connections cannot be used by services.',
    'id_default_query_timeout': 'How long to wait for a response,<br>in seconds.',
    'id_address': 'Full URL to the GraphQL endpoint,<br>including the path.',
    'id_security_id': 'Security definition used to authenticate<br>requests to the GraphQL server.',
    'id_extra': 'Custom HTTP headers sent with every request<br>as a JSON object, e.g. {"X-Tenant": "acme"}.',
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new GraphQL connection', null);
    $.fn.zato.how_it_works.init({
        badge_id: 'create-how-it-works',
        div_id: '#create-div',
        descriptions: $.fn.zato.outgoing.graphql.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the GraphQL connection', id);
    $.fn.zato.how_it_works.init({
        badge_id: 'edit-how-it-works',
        div_id: '#edit-div',
        descriptions: $.fn.zato.outgoing.graphql.field_descriptions
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.data_table.new_row = function(item, data, include_tr) {
    let row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    let is_active = item.is_active == true;
    var security_name = item.security_id ? item.security_select : '<span class="form_hint">---</span>';

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td><a href="{0}">{0}</a></td>', item.address);

    // 2
    row += String.format("<td>{0}</td>", security_name || $.fn.zato.empty_value);

    // 3
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.graphql.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.graphql.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.graphql.invoke('{0}')\">Invoke</a>", item.id));

    // 4
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", item.is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.extra);
    row += String.format("<td class='ignore'>{0}</td>", item.default_query_timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.security_id);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'GraphQL connection `{0}` deleted',
        'Are you sure you want to delete GraphQL connection `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.get_invoke_url = function(id) {
    return '/zato/outgoing/graphql/invoke/' + id + '/';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.invoke = function(id) {
    var item = $.fn.zato.data_table.data[id];
    if (!item) {
        return;
    }

    var history_key = 'zato.invoke-history.outconn-graphql.' + id;

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        connection: 'outconn-graphql',
        history_key: history_key,
        highlight_lexer: 'graphql',
        get_invoke_url_func: $.fn.zato.outgoing.graphql.get_invoke_url,
        collect_form_data_func: $.fn.zato.outgoing.graphql.collect_form_data
    });

    var default_query = 'query IntrospectionQuery {\n  __schema {\n    types {\n      name\n      kind\n      description\n    }\n  }\n}';
    var old_default_query = '{\n  __schema {\n    types {\n      name\n    }\n  }\n}';

    var current_val = $('#invoker-modal-request').val();
    if (!current_val || current_val === old_default_query) {
        $('#invoker-modal-request').val(default_query);
    }

    $('#invoker-modal-request').attr('placeholder',
        'Enter a GraphQL query\n\nCtrl+Enter to invoke, Ctrl+K for history');

    // Set up the transparent-textarea + highlight-layer overlay
    $.fn.zato.outgoing.graphql._setup_request_highlight();

    $('#invoker-more-options').html(
        '<div class="invoker-more-options-row" style="gap:4px">'
        + '<label>Variables</label>'
        + '<textarea id="invoker-modal-variables" rows="2" placeholder=\'{"userId": 1}\'></textarea>'
        + '</div>'
    );

    var saved = $.fn.zato.invoker._load_overlay_state(history_key);
    if (saved.variables) {
        $('#invoker-modal-variables').val(saved.variables);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql._highlight_debounce_timer = null;

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql._setup_request_highlight = function() {

    var textarea = $('#invoker-modal-request');

    // Wrap the textarea in a container if not already wrapped
    if (!textarea.parent().hasClass('invoker-request-highlight-container')) {

        textarea.wrap('<div class="invoker-request-highlight-container"></div>');
        textarea.after('<pre class="invoker-request-highlight-layer syntax-monokai" id="invoker-request-highlight-pre"></pre>');
    }

    // Run the initial highlight ..
    $.fn.zato.outgoing.graphql._sync_request_highlight();

    // .. bind input events: immediate plain-text echo + debounced Pygments call ..
    textarea.off('input.graphql_highlight').on('input.graphql_highlight', function() {
        var text = textarea.val();
        var highlight_pre = $('#invoker-request-highlight-pre');

        // Show escaped plain text immediately so keystrokes are always visible
        if (text) {
            highlight_pre.text(text + '\n');
        } else {
            highlight_pre.html('\n');
        }

        clearTimeout($.fn.zato.outgoing.graphql._highlight_debounce_timer);
        $.fn.zato.outgoing.graphql._highlight_debounce_timer = setTimeout(
            $.fn.zato.outgoing.graphql._sync_request_highlight, 300
        );
    });

    // .. and sync scroll between textarea and pre.
    textarea.off('scroll.graphql_highlight').on('scroll.graphql_highlight', function() {
        var highlight_pre = document.getElementById('invoker-request-highlight-pre');
        highlight_pre.scrollTop = this.scrollTop;
        highlight_pre.scrollLeft = this.scrollLeft;
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql._sync_request_highlight = function() {
    var textarea = $('#invoker-modal-request');
    var text = textarea.val();
    var highlight_pre = $('#invoker-request-highlight-pre');

    if (!text) {
        highlight_pre.html('\n');
        return;
    }

    // Show plain text immediately so the content is always visible
    highlight_pre.text(text + '\n');

    $.ajax({
        type: 'POST',
        url: '/zato/highlight/',
        data: {text: text, lexer: 'graphql'},
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        dataType: 'json',
        success: function(data) {
            highlight_pre.html(data.html + '\n');
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.collect_form_data = function() {
    return {
        'data-request': $('#invoker-modal-request').val(),
        'variables': $('#invoker-modal-variables').val(),
    };
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Live form updates registration
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.live_form_updates.register('create', [
    {object_type: 'security', target_select: '#id_security_id', label_format: '{sec_type_name}/{name}'}
]);

$.fn.zato.live_form_updates.register('edit', [
    {object_type: 'security', target_select: '#id_edit-security_id', label_format: '{sec_type_name}/{name}'}
]);

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
