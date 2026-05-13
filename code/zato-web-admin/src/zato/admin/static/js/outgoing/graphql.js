
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.GraphQLOutconn = new Class({
    toString: function() {
        var description = '<GraphQLOutconn id:{0} name:{1} is_active:{2}>';

        var out = String.format(description,
            this.id ? this.id : '(none)',
            this.name ? this.name : '(none)',
            this.is_active ? this.is_active : '(none)');

        return out;
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
    var uniqueConstraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(uniqueConstraints, function(constraintIdx, constraint) {
        $.fn.zato.validate_unique('#id_' + constraint.field, constraint.entity_type, constraint.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + constraint.field, constraint.entity_type, constraint.attr_name);
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

$.fn.zato.outgoing.graphql.data_table.new_row = function(item, data, includeTR) {
    let row = '';

    if(includeTR) {
        row += String.format('<tr id=\'tr_{0}\' class=\'updated\'>', item.id);
    }

    let isActive = item.is_active == true;

    var securityCell = '<span class="form_hint">---</span>';
    var secType = '';
    var selectedValue = $('#id_security_id').val() || $('#id_edit-security_id').val() || '';

    if(item.security_id && selectedValue && selectedValue.indexOf('/') > -1) {
        secType = selectedValue.split('/')[0];
        var secName = item.security_id_select ? item.security_id_select.split('/').slice(1).join('/') : '';

        var secHref = '/zato/security/';
        if(secType === 'oauth') {
            secHref += 'oauth/outconn/client-credentials/';
        }
        else if(secType === 'basic_auth') {
            secHref += 'basic-auth/';
        }
        else if(secType === 'apikey') {
            secHref += 'apikey/';
        }
        secHref += '?cluster=1&query=' + encodeURIComponent(secName);
        securityCell = String.format('<a href=\'{0}\'>{1}</a>', secHref, secName);
    }

    row += '<td class=\'numbering\'>&nbsp;</td>';
    row += '<td class=\'impexp\'><input type=\'checkbox\' /></td>';

    // 1
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', isActive ? 'Yes' : 'No');
    row += String.format('<td><a href=\'{0}\'>{0}</a></td>', item.address);

    // 2
    row += String.format('<td>{0}</td>', securityCell);

    // 3
    var editLink = String.format('<a href=\'javascript:$.fn.zato.outgoing.graphql.edit(\x27{0}\x27)\'>Edit</a>', item.id);
    row += String.format('<td>{0}</td>', editLink);

    var deleteLink = String.format('<a href=\'javascript:$.fn.zato.outgoing.graphql.delete_(\x27{0}\x27);\'>Delete</a>', item.id);
    row += String.format('<td>{0}</td>', deleteLink);

    var pingLink = String.format('<a href=\'javascript:void(0)\' onclick=\'$.fn.zato.data_table.ping(\x27{0}\x27, this)\'>Ping</a>', item.id);
    row += String.format('<td>{0}</td>', pingLink);

    var invokeLink = String.format('<a href=\'javascript:$.fn.zato.outgoing.graphql.invoke(\x27{0}\x27)\'>Invoke</a>', item.id);
    row += String.format('<td>{0}</td>', invokeLink);

    // 4
    row += String.format('<td class=\'ignore item_id_{0}\'>{0}</td>', item.id);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.is_active);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.extra);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.default_query_timeout);
    row += String.format('<td class=\'ignore\'>{0}</td>', item.security_id);
    row += String.format('<td class=\'ignore\'>{0}</td>', secType);

    if(includeTR) {
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

    var out = '/zato/outgoing/graphql/invoke/' + id + '/';
    return out;
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql.invoke = function(id) {
    var item = $.fn.zato.data_table.data[id];
    if (!item) {
        return;
    }

    var historyKey = 'zato.invoke-history.outconn-graphql.' + id;

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        connection: 'outconn-graphql',
        history_key: historyKey,
        highlight_lexer: 'graphql',
        get_invoke_url_func: $.fn.zato.outgoing.graphql.get_invoke_url,
        collect_form_data_func: $.fn.zato.outgoing.graphql.collect_form_data
    });

    var defaultQuery = 'query IntrospectionQuery {\n  __schema {\n    types {\n      name\n      kind\n      description\n    }\n  }\n}';

    var currentValue = $('#invoker-modal-request').val();
    if (!currentValue) {
        $('#invoker-modal-request').val(defaultQuery);
    }

    $('#invoker-modal-request').attr('placeholder',
        'Enter a GraphQL query\n\nCtrl+Enter to invoke, Ctrl+K for history');

    // Set up the transparent-textarea + highlight-layer overlay
    $.fn.zato.outgoing.graphql._setupRequestHighlight();

    $('#invoker-more-options').html(
        '<div class="invoker-more-options-row invoker-more-options-row-compact">'
        + '<label>Variables</label>'
        + '<textarea id="invoker-modal-variables" rows="2" placeholder=\'{"userId": 1}\'></textarea>'
        + '</div>'
    );

    var saved = $.fn.zato.invoker._load_overlay_state(historyKey);
    if (saved.variables) {
        $('#invoker-modal-variables').val(saved.variables);
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql._debounceTimer = null;

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql._setupRequestHighlight = function() {

    var textarea = $('#invoker-modal-request');

    // Wrap the textarea in a container if not already wrapped ..
    if (!textarea.parent().hasClass('invoker-request-highlight-container')) {

        textarea.wrap('<div class="invoker-request-highlight-container"></div>');
        textarea.after('<pre class="invoker-request-highlight-layer syntax-monokai" id="invoker-request-highlight-pre"></pre>');
    }

    // .. run the initial highlight ..
    $.fn.zato.outgoing.graphql._syncRequestHighlight();

    // .. bind input events: immediate plain-text echo + debounced Pygments call ..
    textarea.off('input.graphql_highlight');

    textarea.on('input.graphql_highlight', function() {
        var text = textarea.val();
        var highlightPre = $('#invoker-request-highlight-pre');

        // Show escaped plain text immediately so keystrokes are always visible
        if (text) {
            highlightPre.text(text + '\n');
        }
        else {
            highlightPre.html('\n');
        }

        clearTimeout($.fn.zato.outgoing.graphql._debounceTimer);
        $.fn.zato.outgoing.graphql._debounceTimer = setTimeout(
            $.fn.zato.outgoing.graphql._syncRequestHighlight, 300
        );
    });

    // .. and sync scroll between textarea and pre.
    textarea.off('scroll.graphql_highlight');

    textarea.on('scroll.graphql_highlight', function() {
        var highlightPre = document.getElementById('invoker-request-highlight-pre');
        highlightPre.scrollTop = this.scrollTop;
        highlightPre.scrollLeft = this.scrollLeft;
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.graphql._syncRequestHighlight = function() {
    var textarea = $('#invoker-modal-request');
    var text = textarea.val();
    var highlightPre = $('#invoker-request-highlight-pre');

    if (!text) {
        highlightPre.html('\n');
        return;
    }

    // Show plain text immediately so the content is always visible
    highlightPre.text(text + '\n');

    // .. then replace with server-side highlighted HTML.
    $.fn.zato.highlightElement(highlightPre, text, 'graphql');
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
