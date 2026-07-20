
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

$.fn.zato.outgoing.llm.config = {
    'custom_label': 'Custom',
    'custom_value': 'zato-custom-model'
};

// /////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.password_required = false;
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.LLM;
    $.fn.zato.data_table.new_row_func = $.fn.zato.outgoing.llm.data_table.new_row;
    $.fn.zato.data_table.parse();
    $.fn.zato.data_table.setup_forms(['name', 'address', 'model', 'pool_size', 'timeout', 'max_tokens',
        'max_history_turns', 'chat_expiry']);
    var unique_constraints = [
        {field: 'name', entity_type: 'generic_connection', attr_name: 'name'}
    ];
    $.each(unique_constraints, function(i, c) {
        $.fn.zato.validate_unique('#id_' + c.field, c.entity_type, c.attr_name);
        $.fn.zato.validate_unique('#id_edit-' + c.field, c.entity_type, c.attr_name);
    });

    // Maps each catalog model's wire id to its provider, for address auto-fill
    $.fn.zato.outgoing.llm.model_providers = {};
    $.each($.fn.zato.outgoing.llm.models, function(ignored, model) {
        $.fn.zato.outgoing.llm.model_providers[model.id] = model.provider;
    });

    $.fn.zato.outgoing.llm.init_model_select('create');
    $.fn.zato.outgoing.llm.init_model_select('edit');

    // A hand-edited address decides on its own whether the API key is still required
    $.fn.zato.outgoing.llm.get_address_input('create').on('input', function() {
        $.fn.zato.outgoing.llm.update_secret_required('create');
    });

    // Typing a key makes the field non-empty, so any "required field" attention goes away
    $('#id_secret').on('input', function() {
        if($(this).val()) {
            $.fn.zato.cleanup_elem_css_attention($(this));
        }
    });
})

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.llm.field_descriptions = {
    'id_name': 'A unique name for this connection.<br>Services look it up by this name<br>through self.llm[name].',
    'id_is_active': 'Whether this connection can be used.<br>Services cannot look up an inactive connection.',
    'id_pool_size': 'How many HTTP clients the pool keeps ready.<br>Each concurrent call checks one out.',
    'id_model': 'The model every call through this connection uses.<br>Pick one from the list or choose Custom and enter<br>any name by hand - any OpenAI-compatible API<br>and model works, e.g. Ollama, vLLM or LiteLLM.',
    'id_address': 'The base URL of the API to call.<br>It follows the model you pick and you can<br>point it at any self-hosted or proxy endpoint.',
    'id_secret': 'The API key sent with each call.<br>Required for hosted providers while self-hosted<br>endpoints may not need one. Later on, it can be<br>updated with the Change API key link.',
    'id_timeout': 'How many seconds to wait<br>for the provider\'s response.',
    'id_max_tokens': 'The most tokens the model may generate<br>per reply, sent to providers that require it.',
    'id_max_history_turns': 'How many past turns of a chat are sent<br>to the provider - a turn is one user message<br>plus the assistant\'s reply. Older turns stay<br>in the cache until they expire.',
    'id_chat_expiry': 'How many seconds a chat\'s history<br>is kept in the cache after its last message.',
};

// /////////////////////////////////////////////////////////////////////////////

// Returns the model text input of a form
$.fn.zato.outgoing.llm.get_model_input = function(form_type) {
    var prefix = form_type == 'edit' ? 'edit-' : '';
    return $('#id_' + prefix + 'model');
}

// Returns the address input of a form
$.fn.zato.outgoing.llm.get_address_input = function(form_type) {
    var prefix = form_type == 'edit' ? 'edit-' : '';
    return $('#id_' + prefix + 'address');
}

// /////////////////////////////////////////////////////////////////////////////

// Returns true if the address is one of the provider defaults
$.fn.zato.outgoing.llm.is_default_address = function(value) {
    var out = false;
    $.each($.fn.zato.outgoing.llm.addresses, function(ignored, address) {
        if(value == address) {
            out = true;
        }
    });
    return out;
}

// Replaces a form's address only when the user has not customized it -
// an empty address or one of the provider defaults is fair game,
// anything entered by hand is left alone.
$.fn.zato.outgoing.llm.update_address = function(form_type, new_value) {
    var address_input = $.fn.zato.outgoing.llm.get_address_input(form_type);
    var current = address_input.val();
    if(current == '' || $.fn.zato.outgoing.llm.is_default_address(current)) {
        address_input.val(new_value);

        // A freshly filled-in address is valid again, so any earlier
        // "required field" attention must go away with it.
        if(new_value) {
            $.fn.zato.cleanup_elem_css_attention(address_input);
        }
    }

    // Whether the key is needed follows from where the address points now
    $.fn.zato.outgoing.llm.update_secret_required(form_type);
}

// /////////////////////////////////////////////////////////////////////////////

// Hosted providers always demand a key while self-hosted endpoints may not,
// so the create form's API key is required exactly when the address
// points at one of the provider defaults. The edit form has no key field
// at all - keys are changed there through the Change API key link.
$.fn.zato.outgoing.llm.update_secret_required = function(form_type) {

    if(form_type != 'create') {
        return;
    }

    var secret_input = $('#id_secret');
    var address = $.fn.zato.outgoing.llm.get_address_input(form_type).val();

    // The validator selects fields by the data-zato-validator-required attribute,
    // not by the required class, so it is the attribute that has to be toggled here.
    if($.fn.zato.outgoing.llm.is_default_address(address)) {
        secret_input.addClass('required');
        $.fn.zato.data_table.set_field_required('#id_secret');
    }
    else {
        secret_input.removeClass('required');
        $.fn.zato.data_table.remove_field_required('#id_secret');
        $.fn.zato.cleanup_elem_css_attention(secret_input);
    }
}

// /////////////////////////////////////////////////////////////////////////////

// Fills a form's model select with the catalog models plus Custom and wires it
// to the model text input - the input is what is submitted, the select drives it.
$.fn.zato.outgoing.llm.init_model_select = function(form_type) {

    var select = $('#llm-model-select-' + form_type);
    var input = $.fn.zato.outgoing.llm.get_model_input(form_type);

    // The options show the friendly names but carry the wire ids the input receives
    $.each($.fn.zato.outgoing.llm.models, function(ignored, model) {
        select.append($('<option/>').attr('value', model.id).text(model.name));
    });
    select.append($('<option/>')
        .attr('value', $.fn.zato.outgoing.llm.config.custom_value)
        .text($.fn.zato.outgoing.llm.config.custom_label));

    // Picking a catalog model fills in both the input and the provider's address,
    // picking Custom clears the input so a model id can be entered by hand -
    // in both cases the address changes only if the user has not customized it.
    select.on('change', function() {
        var selected = select.val();
        if(selected == $.fn.zato.outgoing.llm.config.custom_value) {
            input.val('');
            input.trigger('focus');
            $.fn.zato.outgoing.llm.update_address(form_type, '');
        }
        else {
            input.val(selected);

            // The input is filled in now, so any earlier "required field" attention must go away
            $.fn.zato.cleanup_elem_css_attention(input);

            var provider = $.fn.zato.outgoing.llm.model_providers[selected];
            $.fn.zato.outgoing.llm.update_address(form_type, $.fn.zato.outgoing.llm.addresses[provider]);
        }
    });

    // Editing the input by hand flips the select to Custom the moment the text
    // no longer matches a catalog model, so the select never misrepresents the input.
    // Only a change of the select's state may touch the address - keystrokes that
    // keep the state as it was must not keep clearing what the user typed in.
    input.on('input', function() {

        // Typing anything makes the input non-empty, so the "required field" attention goes away
        if(input.val()) {
            $.fn.zato.cleanup_elem_css_attention(input);
        }

        var before = select.val();
        $.fn.zato.outgoing.llm.sync_model_select(form_type);
        var after = select.val();

        if(after != before) {
            if(after == $.fn.zato.outgoing.llm.config.custom_value) {
                $.fn.zato.outgoing.llm.update_address(form_type, '');
            }
            else {
                var provider = $.fn.zato.outgoing.llm.model_providers[after];
                $.fn.zato.outgoing.llm.update_address(form_type, $.fn.zato.outgoing.llm.addresses[provider]);
            }
        }
    });
}

// /////////////////////////////////////////////////////////////////////////////

// Points a form's model select at the entry matching the model input's wire id,
// falling back to Custom for anything typed in by hand.
$.fn.zato.outgoing.llm.sync_model_select = function(form_type) {

    var select = $('#llm-model-select-' + form_type);
    var input = $.fn.zato.outgoing.llm.get_model_input(form_type);
    var value = input.val();

    if(value in $.fn.zato.outgoing.llm.model_providers) {
        select.val(value);
    }
    else {
        select.val($.fn.zato.outgoing.llm.config.custom_value);
    }
}

// /////////////////////////////////////////////////////////////////////////////

// A dialog always opens with its More options block collapsed,
// no matter what state the previous open left it in.
$.fn.zato.outgoing.llm.collapse_more_options = function(form_type) {
    $('.llm-more-options-' + form_type).each(function(ignored, elem) {
        $.fn.zato.toggle_visible_hidden(elem, false);
    });
}

// /////////////////////////////////////////////////////////////////////////////

$.fn.zato.outgoing.llm.create = function() {
    $.fn.zato.data_table._create_edit('create', 'Create a new outgoing LLM connection', null);
    $.fn.zato.outgoing.llm.sync_model_select('create');
    $.fn.zato.outgoing.llm.collapse_more_options('create');
    $.fn.zato.outgoing.llm.update_secret_required('create');
    $.fn.zato.how_it_works.init({
        badgeId: 'create-how-it-works',
        divId: '#create-div',
        descriptions: $.fn.zato.outgoing.llm.field_descriptions
    });
}

$.fn.zato.outgoing.llm.edit = function(id) {
    $.fn.zato.data_table._create_edit('edit', 'Update the outgoing LLM connection', id);
    $.fn.zato.outgoing.llm.sync_model_select('edit');
    $.fn.zato.outgoing.llm.collapse_more_options('edit');
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

    row += "<td class='numbering'>&nbsp;</td>";
    row += "<td class='impexp'><input type='checkbox' /></td>";
    row += String.format('<td>{0}</td>', item.name);
    row += String.format('<td>{0}</td>', is_active ? 'Yes' : 'No');
    row += String.format('<td>{0}</td>', item.model);
    row += String.format('<td>{0}</td>', item.address);
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.data_table.change_password('{0}')\">Change API key</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.llm.edit('{0}')\">Edit</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:$.fn.zato.outgoing.llm.delete_('{0}');\">Delete</a>", item.id));
    row += String.format('<td>{0}</td>', String.format("<a href=\"javascript:void(0)\" onclick=\"$.fn.zato.data_table.ping('{0}', this)\">Ping</a>", item.id));
    row += String.format("<td class='ignore item_id_{0}'>{0}</td>", item.id);
    row += String.format("<td class='ignore'>{0}</td>", is_active);
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
