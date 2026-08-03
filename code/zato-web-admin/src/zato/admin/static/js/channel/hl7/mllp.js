
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.data_table.HL7MLLPChannel = new Class({
    toString: function() {
        var s = '<HL7MLLPChannel id:{0} name:{1} is_active:{2}>';
        return String.format(s, this.id ? this.id : '(none)',
                                this.name ? this.name : '(none)',
                                this.is_active ? this.is_active : '(none)');
    }
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(document).ready(function() {
    $('#data-table').tablesorter();
    $.fn.zato.data_table.class_ = $.fn.zato.data_table.HL7MLLPChannel;
    $.fn.zato.data_table.parse();
    $.fn.zato.channel.hl7.mllp.init_copy_address_link();
    $.fn.zato.channel.hl7.mllp.row_edit.init();
    $.fn.zato.channel.hl7.mllp.init_hints();
})

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.delete_ = function(id) {
    $.fn.zato.data_table.delete_(id, 'td.item_id_',
        'HL7 MLLP channel `{0}` deleted',
        'Are you sure you want to delete HL7 MLLP channel `{0}`?',
        true);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.config = {
    cluster_id: '1',
    import_demo_url: '/zato/channel/hl7/mllp/import-demo-config',

    // The ports feeds connect on, written in by the page from what the environment has
    mllp_port: '',
    mllps_port: '',

    // What each endpoint is called, which button in the popup carries it and the address
    // it hands over, the address filled in once the page knows what name it was reached by
    mllp_label: 'MLLP',
    mllps_label: 'MLLPS',
    mllp_button_id: 'mllp-copy-address-plain',
    mllps_button_id: 'mllp-copy-address-tls',
    mllp_address: '',
    mllps_address: '',

    // What the popup hangs off, and which side of a button in it the copy flash goes on,
    // the button having the popup's own arrow directly above it
    copy_address_link_id: 'mllp-copy-address-link',
    copied_flash_placement: 'right',

    // Where a row goes when it is edited where it stands, its id following it
    inline_edit_url: '/zato/channel/hl7/mllp/inline-edit/',

    // Where a service is opened, and what a cell with nothing in it says instead
    service_ide_url: '/zato/service/ide/service/{name}/?cluster=1',
    empty_cell_label: 'Click to add',

    // What a cell says in passing when the pointer rests on it, and how patiently
    open_hint_label: 'Click to open',
    paused_hint_label: ' (paused)',
    hint_theme: 'zato-hint',
    hint_placement: 'right',
    hint_delay: [250, 100],

    // How long a confirmation takes to fade once it has been read
    confirmation_fade_ms: 200,

    // What the two flags read as, in the order a boolean puts them
    flag_labels: ['No', 'Yes']
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.copy_endpoint_address = function(endpoint) {

    var config = $.fn.zato.channel.hl7.mllp.config;
    var button = document.getElementById(config[endpoint + '_button_id']);

    // Pressed, the button hands the address over and says so beside itself for a moment
    $.fn.zato.ui_helpers.copy_to_clipboard(button, config[endpoint + '_address'], config.copied_flash_placement);
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.init_copy_address_link = function() {

    var config = $.fn.zato.channel.hl7.mllp.config;

    // Whichever of this machine's names got the browser here is the one a feed on the same
    // network reaches it by, so the page never has to be told what to call itself
    var host = window.location.hostname;

    config.mllp_address = host + ':' + config.mllp_port;
    config.mllps_address = host + ':' + config.mllps_port;

    var content = `
        <div class="zato-tippy-buttons">
            <input type="button" id="${config.mllp_button_id}" value="${config.mllp_label} ${config.mllp_address}" onclick="$.fn.zato.channel.hl7.mllp.copy_endpoint_address('mllp');"/>
            <input type="button" id="${config.mllps_button_id}" value="${config.mllps_label} ${config.mllps_address}" onclick="$.fn.zato.channel.hl7.mllp.copy_endpoint_address('mllps');"/>
        </div>
    `;

    tippy('#' + config.copy_address_link_id, {
        content: content,
        allowHTML: true,
        theme: 'light',
        trigger: 'click',
        placement: 'bottom',
        arrow: true,
        interactive: true,
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Everything a row changes without leaving the page, worded the way every inline edit is
$.fn.zato.channel.hl7.mllp.inline = {};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Says beside a row that it went through, for as long as that takes to read
$.fn.zato.channel.hl7.mllp.inline.flash = function(link, message) {

    var config = $.fn.zato.inline_edit.config;

    var instance = tippy(link, {
        content: message,
        theme: 'dark',
        trigger: 'manual',
        placement: config.confirmation_placement,
        hideOnClick: false,
        allowHTML: false
    });

    instance.show();

    // The tooltip leaves nothing of itself behind
    setTimeout(function() {
        instance.hide();
        setTimeout(function() {
            instance.destroy();
        }, $.fn.zato.channel.hl7.mllp.config.confirmation_fade_ms);
    }, config.saved_hide_ms);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Sends what one row changed and hands the answer over to whoever asked for the save
$.fn.zato.channel.hl7.mllp.inline.save = function(link, id, data, on_saved, saved_label) {

    var config = $.fn.zato.inline_edit.config;
    var url = $.fn.zato.channel.hl7.mllp.config.inline_edit_url + id + '/';

    $.fn.zato.action_runner.run({
        link_elem: link,
        url: url,
        data: data,
        spinner_label: config.saving_label,
        details_modal_title: config.details_modal_title,
        show_delay_ms: config.saving_lead_in_ms,

        // The endpoint answers with JSON when it saved and with an error page when it did not
        parse: function(jqXHR) {

            var is_http_ok = (jqXHR.status >= 200 && jqXHR.status < 300);

            return {
                is_success: is_http_ok,
                label: is_http_ok ? saved_label : config.error_label,
                details_title: config.error_label,
                details_body: jqXHR.responseText,
                jqXHR: jqXHR
            };
        },

        on_success: function(instance, result) {

            // The spinner makes way for the confirmation
            instance.hide();
            instance.destroy();

            on_saved(JSON.parse(result.jqXHR.responseText));

            $.fn.zato.channel.hl7.mllp.inline.flash(link, saved_label);
        }
    });
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Yes or No, the way a row shows a flag of its own
$.fn.zato.channel.hl7.mllp.flag_label = function(value) {
    var out = $.fn.zato.channel.hl7.mllp.config.flag_labels[value ? 1 : 0];
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Turns one flag of one row over, the opposite of what the row stands at being what is sent
$.fn.zato.channel.hl7.mllp.toggle_flag = function(id, link, name, after_saved) {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var instance = $.fn.zato.data_table.data[id];

    var data = {};
    data[name] = !$.fn.zato.to_bool(instance[name]);

    var on_saved = function(saved) {

        // The row stands at what came back
        instance[name] = saved[name];
        link.textContent = mllp.flag_label(saved[name]);

        after_saved(saved);
    };

    mllp.inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.toggle_active = function(id, link) {

    // Nothing else on the list changes when one channel is switched on or off
    var after_saved = function() {};

    $.fn.zato.channel.hl7.mllp.toggle_flag(id, link, 'is_active', after_saved);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Says which row another channel's messages go to when none of the matchers takes them
$.fn.zato.channel.hl7.mllp.toggle_default = function(id, link) {

    var mllp = $.fn.zato.channel.hl7.mllp;

    var after_saved = function(saved) {

        // The row that held the flag before has just lost it
        if(saved.default_cleared_id) {
            mllp.clear_default_cell(saved.default_cleared_id);
        }
    };

    mllp.toggle_flag(id, link, 'is_default', after_saved);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Turns another row's Default cell over, it having lost the flag to the one just saved
$.fn.zato.channel.hl7.mllp.clear_default_cell = function(id) {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var instance = $.fn.zato.data_table.data[id];

    instance.is_default = false;

    var row = $('.item_id_' + id).closest('tr');
    var cell_link = row.find('a[onclick*="toggle_default"]');

    cell_link.text(mllp.flag_label(false));
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The Service and Destinations columns - a row's target is edited in the wizard's own panels,
// which read their state and their fields off one object, so this page fills that object in.
$.fn.zato.channel.hl7.mllp.row_edit = {

    config: {

        // What the fields the panels read and write are named after
        field_prefix: 'mllp-row',

        // Where the panels draw their chips, out of sight - the cells say it all
        slots: {
            destinations: 'mllp-row-slot-destinations',
            service: 'mllp-row-slot-service',
            delivery: 'mllp-row-slot-delivery',
            reply: 'mllp-row-slot-reply'
        },

        // What a row that says nothing of either falls back on, the delivery modes
        // being named in the module that draws them
        default_delivery: 'same-time',

        // The row being edited, the cell its panel hangs off, and what it opened on
        row: null,
        link: null,
        baseline: null
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the panels hold, filled in from the row each time one is opened
$.fn.zato.channel.hl7.mllp.wizard.state = {
    destinationList: [],
    delivery: $.fn.zato.channel.hl7.mllp.row_edit.config.default_delivery,
    respondFrom: $.fn.zato.destinations.config.respondFromService
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The fields the wizard's panels edit a row through
$.fn.zato.channel.hl7.mllp.wizard.field = function(name) {
    var out = $('#id_' + $.fn.zato.channel.hl7.mllp.row_edit.config.field_prefix + '-' + name);
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Every panel ends in a render, which is where the page learns the row changed
$.fn.zato.channel.hl7.mllp.wizard.review.refreshSummaries = function() {
    $.fn.zato.channel.hl7.mllp.row_edit.on_changed();
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.row_edit.init = function() {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var destinations = mllp.wizard.destinations;

    destinations.config.slots = mllp.row_edit.config.slots;

    // The connections are on their way before the first panel opens
    destinations.init();
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the fields hold, which is what a row is saved with
$.fn.zato.channel.hl7.mllp.row_edit.read_target = function() {

    var wizard = $.fn.zato.channel.hl7.mllp.wizard;

    var out = {
        service: wizard.field('service').val(),
        destinations: wizard.field('destinations').val(),
        respond_from: wizard.field('respond_from').val(),
        delivery_mode: wizard.field('delivery_mode').val()
    };

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Opens one of the two panels on the row the cell belongs to
$.fn.zato.channel.hl7.mllp.row_edit.open = function(link, panel) {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var wizard = mllp.wizard;
    var row_edit = mllp.row_edit;
    var config = row_edit.config;

    var row = document.getElementById('tr_' + link.dataset.id);

    wizard.field('service').val(row.dataset.service);
    wizard.field('destinations').val(row.dataset.destinations);
    wizard.field('respond_from').val(row.dataset.respondFrom);
    wizard.field('delivery_mode').val(row.dataset.deliveryMode);

    // A row saying nothing of either is not left with what the row before it said
    wizard.state.delivery = config.default_delivery;
    wizard.state.respondFrom = $.fn.zato.destinations.config.respondFromService;

    wizard.destinations.deserialize();
    wizard.destinations.serialize();

    config.row = row;
    config.link = link;
    config.baseline = row_edit.read_target();

    $.fn.zato.wizard_kit.lines.openPanel(link, panel);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.row_edit.open_service = function(link) {
    var panels = $.fn.zato.channel.hl7.mllp.wizard.destinations.panels;
    $.fn.zato.channel.hl7.mllp.row_edit.open(link, panels.servicePanel());
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.row_edit.open_destinations = function(link) {
    var panels = $.fn.zato.channel.hl7.mllp.wizard.destinations.panels;
    $.fn.zato.channel.hl7.mllp.row_edit.open(link, panels.destinationsPanel());
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Saves the row whose panel has just answered, a panel closed on what it opened with saving nothing
$.fn.zato.channel.hl7.mllp.row_edit.on_changed = function() {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var row_edit = mllp.row_edit;
    var config = row_edit.config;
    var baseline = config.baseline;

    // The page renders once on its own, before any row has been opened
    if(!baseline) {
        return;
    }

    mllp.wizard.destinations.serialize();

    var data = row_edit.read_target();

    var is_same = data.service === baseline.service &&
        data.destinations === baseline.destinations &&
        data.respond_from === baseline.respond_from &&
        data.delivery_mode === baseline.delivery_mode;

    if(is_same) {
        return;
    }

    var row = config.row;
    var link = config.link;

    var on_saved = function(saved) {
        config.baseline = data;
        row_edit.update_row(link.dataset.id, row, data, saved);
    };

    mllp.inline.save(link, link.dataset.id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the two cells and the row now stand at
$.fn.zato.channel.hl7.mllp.row_edit.update_row = function(id, row, data, saved) {

    var empty = $.fn.zato.channel.hl7.mllp.config.empty_cell_label;

    row.dataset.service = saved.service;
    row.dataset.destinations = data.destinations;
    row.dataset.respondFrom = data.respond_from;
    row.dataset.deliveryMode = data.delivery_mode;

    var service_cell = document.getElementById('mllp-service-' + id);
    service_cell.textContent = saved.service ? saved.service : empty;

    var destinations_cell = document.getElementById('mllp-destinations-' + id);
    destinations_cell.textContent = saved.destination_count ? saved.destination_count : empty;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The link a service is opened by, which is nowhere in the cell, so no column changes width
$.fn.zato.channel.hl7.mllp.service_hint = function(link) {

    var config = $.fn.zato.channel.hl7.mllp.config;
    var row = document.getElementById('tr_' + link.dataset.id);
    var name = row.dataset.service;

    if(!name) {
        return null;
    }

    var out = document.createElement('a');
    out.className = 'zato-hint-line';
    out.href = config.service_ide_url.replace('{name}', encodeURIComponent(name));
    out.textContent = config.open_hint_label;

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What a destination is called where it is listed, the shared module naming the kinds
$.fn.zato.channel.hl7.mllp.destination_type_label = function(type) {

    var typeList = $.fn.zato.destinations.config.typeList;
    var out = '';

    for(var typeIdx = 0; typeIdx < typeList.length; typeIdx++) {
        if(typeList[typeIdx].id === type) {
            out = typeList[typeIdx].label;
        }
    }

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// What the channel delivers to, one line each
$.fn.zato.channel.hl7.mllp.destinations_hint = function(link) {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var row = document.getElementById('tr_' + link.dataset.id);
    var stored = row.dataset.destinations;

    if(!stored) {
        return null;
    }

    var entries = JSON.parse(stored);
    var out = document.createElement('div');

    for(var entryIdx = 0; entryIdx < entries.length; entryIdx++) {

        var entry = entries[entryIdx];
        var text = mllp.destination_type_label(entry.type) + ' - ' + entry.connection;

        if(!entry.is_active) {
            text += mllp.config.paused_hint_label;
        }

        var line = document.createElement('span');
        line.className = 'zato-hint-line';
        line.textContent = text;

        out.appendChild(line);
    }

    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.init_hints = function() {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var config = mllp.config;

    // A cell with nothing in it has nothing to say, so its hint never opens
    var build = function(get_content) {

        var out = function(instance) {

            var content = get_content(instance.reference);

            if(!content) {
                return false;
            }

            instance.setContent(content);
        };

        return out;
    };

    var options = {
        theme: config.hint_theme,
        placement: config.hint_placement,
        delay: config.hint_delay,
        interactive: true,
        arrow: true,
        appendTo: document.body
    };

    tippy('#data-table a.mllp-service-cell', $.extend({}, options, {onShow: build(mllp.service_hint)}));
    tippy('#data-table a.mllp-destinations-cell', $.extend({}, options, {onShow: build(mllp.destinations_hint)}));
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The Match column - each row's matchers are edited in the very popover the wizard
// edits them in, hosted here on a handful of hidden fields instead of on a wizard form.
$.fn.zato.channel.hl7.mllp.match = {

    // The kit installs the popover engine here
    forms: {},

    config: {

        // Every element the popover makes is named after this
        idPrefix: 'mllp-match',

        // Which micro-form of the ones the kit was given is the one this page opens
        form_name: 'routing',

        // What a saved row is told beside itself
        saved_message: 'OK, matchers saved',

        // The row being edited, held while its popover is open
        link: null
    }
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The hidden fields the popover reads and writes, named the way it expects
$.fn.zato.channel.hl7.mllp.match.field = function(name) {
    var out = $('#id_' + $.fn.zato.channel.hl7.mllp.match.config.idPrefix + '-' + name);
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// A matcher is explained in the same words wherever it is shown, the popover inputs
// carrying ids of their own for the help to find them under
$.fn.zato.channel.hl7.mllp.match.helpDescriptions = function() {
    var match = $.fn.zato.channel.hl7.mllp.match;
    var out = match.forms.helpDescriptions($.fn.zato.channel.hl7.mllp.field_descriptions);
    return out;
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Opens the matchers of one row, the popover hanging off the very line that was clicked
$.fn.zato.channel.hl7.mllp.match.open = function(link) {

    var match = $.fn.zato.channel.hl7.mllp.match;
    var matchers = $.fn.zato.channel.hl7.mllp.matchers;
    var values = JSON.parse(link.dataset.match);

    match.config.link = link;

    for(var fieldIdx = 0; fieldIdx < matchers.fields.length; fieldIdx++) {
        var name = matchers.fields[fieldIdx].field;
        match.field(name).val(values[name]);
    }

    match.forms.open(match.config.form_name, link);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Stores what the popover answered - the whole of a channel is not the page's to send,
// so only the matchers travel and the endpoint puts them into the channel it names
$.fn.zato.channel.hl7.mllp.match.save = function() {

    var match = $.fn.zato.channel.hl7.mllp.match;
    var matchers = $.fn.zato.channel.hl7.mllp.matchers;
    var link = match.config.link;

    var data = {};
    var values = {};

    for(var fieldIdx = 0; fieldIdx < matchers.fields.length; fieldIdx++) {
        var name = matchers.fields[fieldIdx].field;
        var value = match.field(name).val();

        data[name] = value;
        values[name] = value;
    }

    var on_saved = function(saved) {

        // The row now matches on what was just sent, so it says so and opens on it next time
        link.textContent = saved.match_label;
        link.dataset.match = JSON.stringify(values);
    };

    $.fn.zato.channel.hl7.mllp.inline.save(link, link.dataset.id, data, on_saved, match.config.saved_message);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// The popover itself, the matchers and their form coming from the module both this page
// and the wizard build them from - all this page adds is where a saved row goes
$.fn.zato.wizard_kit.forms.setup($.fn.zato.channel.hl7.mllp.match, {
    descriptors: {'routing': $.fn.zato.channel.hl7.mllp.matchers.descriptor},
    showCancel: true,
    doneLabel: 'Save',
    onDone: $.fn.zato.channel.hl7.mllp.match.save
});

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.import_demo_config = function() {
    var config = $.fn.zato.channel.hl7.mllp.config;
    var import_url = config.import_demo_url + '?cluster=' + config.cluster_id;

    var spinner_html = '<div id="import-spinner" style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border: 2px solid #ccc; border-radius: 5px; z-index: 9999;"><div style="display: inline-block; width: 16px; height: 16px; border: 2px solid #ccc; border-top: 2px solid #333; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></div>Importing ...</div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>';
    $('body').append(spinner_html);

    $.ajax({
        url: import_url,
        method: 'POST',
        headers: {'X-CSRFToken': $.cookie('csrftoken')},
        success: function() {
            $('#import-spinner').remove();
            window.location.reload();
        },
        error: function() {
            $('#import-spinner').remove();
            alert('Import failed. Check server logs.');
        }
    });
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp._default_hl7_message = ''
    + 'MSH|^~\\&|WELLNESS_APP|MAIN_FAC|SCHEDULING|MAIN_FAC|20240315120000||ADT^A04^ADT_A01|MSG00001|P|2.9\r'
    + 'EVN|A04|20240315120000\r'
    + 'PID|1||12345^^^FAC^MR||SMITH^JOHN^A||19800115|M\r'
    + 'PV1|1|O\r';

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.get_invoke_url = function(id) {
    return '/zato/channel/hl7/mllp/invoke/' + id + '/';
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.invoke = function(id) {
    var item = $.fn.zato.data_table.data[id];

    $.fn.zato.invoker.open_overlay({
        id: id,
        name: item.name,
        history_key: 'zato.invoke-history.channel-hl7-mllp.' + id,
        get_invoke_url_func: $.fn.zato.channel.hl7.mllp.get_invoke_url,
        show_more_options: false,
        title_prefix: 'Invoke HL7 MLLP channel',
        default_request: $.fn.zato.channel.hl7.mllp._default_hl7_message,
    });

    $.fn.zato.invoker._request_ace_mode = 'ace/mode/hl7';

    var pane = $.fn.zato.invoker._request_pane;
    if (pane) {
        pane.getEditor().session.setMode('ace/mode/hl7');
    }
}

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
