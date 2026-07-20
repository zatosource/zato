
// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.LLM = new Class({
    toString: function() {
        var s = '<LLM id:{0} name:{1} is_active:{2}';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.LLM;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.llm.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'provider', 'address', 'model', 'pool_size', 'timeout', 'max_tokens',
        'max_history_turns', 'chat_expiry']);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });
})

// /////////////////////////////////////////////////////////////////////////////

// Maps provider ids to the names the data table displays
$.fn.zato.outgoing.llm.providerLabels = {
    'openai': 'OpenAI',
    'claude': 'Claude',
    'gemini': 'Gemini'
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.llm.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services look it up by this name<br>through self.llm[name].',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_pool_size': 'How many HTTP clients the pool keeps ready.<br>Each concurrent call checks one out.',
    'id_provider': 'Which API the connection speaks -<br>OpenAI also covers compatible endpoints<br>such as Ollama, vLLM or LiteLLM.',
    'id_address': 'The base URL of the provider\'s API.<br>Point it at a self-hosted or proxy endpoint<br>to use OpenAI-compatible servers.',
    'id_model': 'The model every call through<br>this connection uses.',
    'id_timeout': 'How many seconds to wait<br>for the provider\'s response.',
    'id_max_tokens': 'The most tokens the model may generate<br>per reply, sent to providers that require it.',
    'id_max_history_turns': 'How many past turns of a chat are sent<br>to the provider - a turn is one user message<br>plus the assistant\'s reply. Older turns stay<br>in Redis until they expire.',
    'id_chat_expiry': 'How many seconds a chat\'s history<br>is kept in Redis after its last message.',
};

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.llm.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing LLM connection', null);
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.llm.field_descriptions
    });
}

$.fn.zato.outgoing.llm.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing LLM connection', id);
    $.fn.zato.how_it_works.init({
        badgeId: 'edit-how-it-works',
        divId: '#edit-div',
        descriptions: $.fn.zato.outgoing.llm.field_descriptions
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.llm.data_table.new_row = function(item, data, include_tr) {
    var row = '';

    if(include_tr) {
        row += String.format("<tr id='tr_{0}' class='updated'>", item.id);
    }

    var is_active = item.is_active == true;
    var providerLabel = $.fn.zato.outgoing.llm.providerLabels[item.provider];

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', providerLabel);
    row += String.format('<td>{0}</td>', item.model);
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change API key</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.llm.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.llm.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
    row += String.format("<td class='ignore'>{0}</td>", item.provider);
    row += String.format("<td class='ignore'>{0}</td>", item.pool_size);
    row += String.format("<td class='ignore'>{0}</td>", item.timeout);
    row += String.format("<td class='ignore'>{0}</td>", item.max_tokens);
    row += String.format("<td class='ignore'>{0}</td>", item.max_history_turns);
    row += String.format("<td class='ignore'>{0}</td>", item.chat_expiry);

    if(include_tr) {
        row += '</tr>';
    }

    return row;
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.llm.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'Outgoing LLM connection `{0}` deleted',
        'Are you sure you want to delete outgoing LLM connection `{0}`?',
        true);
}
