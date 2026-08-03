
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

// Everything a row changes without leaving the page goes through here - the two flags and
// the matchers alike. The words, the delay before a spinner appears and the side the
// confirmation goes on are the ones every inline edit in the Dashboard uses.
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

    // The row keeps what it was given, so the tooltip leaves nothing of itself behind
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

        // The endpoint answers with JSON when it saved and with an error page when it did not,
        // so what the answer says of itself is its status code rather than a field of its own
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

            // The spinner makes way for the confirmation, which goes to the side of the link
            // so that it never covers the value that has just changed
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

// Turns one flag of one row over - what the row stands at is what the page already holds
// of it, so the opposite of that is what is sent and what comes back is what it now shows
$.fn.zato.channel.hl7.mllp.toggle_flag = function(id, link, name, after_saved) {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var instance = $.fn.zato.data_table.data[id];

    var data = {};
    data[name] = !$.fn.zato.to_bool(instance[name]);

    var on_saved = function(saved) {

        // The row stands at what came back, both to the eye and to whoever clicks it next
        instance[name] = saved[name];
        link.textContent = mllp.flag_label(saved[name]);

        after_saved(saved);
    };

    mllp.inline.save(link, id, data, on_saved, $.fn.zato.inline_edit.config.saved_label);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$.fn.zato.channel.hl7.mllp.toggle_active = function(id, link) {

    // Nothing about the rest of the list changes when one channel is switched on or off
    var after_saved = function() {};

    $.fn.zato.channel.hl7.mllp.toggle_flag(id, link, 'is_active', after_saved);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Says which row another channel's messages go to when none of the matchers takes them
$.fn.zato.channel.hl7.mllp.toggle_default = function(id, link) {

    var mllp = $.fn.zato.channel.hl7.mllp;

    var after_saved = function(saved) {

        // Only one channel is the default at a time, so the row that held it before
        // has just lost it and says so without the list having to be read again
        if(saved.default_cleared_id) {
            mllp.clear_default_cell(saved.default_cleared_id);
        }
    };

    mllp.toggle_flag(id, link, 'is_default', after_saved);
};

// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Turns another row's Default cell over, that row having lost the flag to the one just saved
$.fn.zato.channel.hl7.mllp.clear_default_cell = function(id) {

    var mllp = $.fn.zato.channel.hl7.mllp;
    var instance = $.fn.zato.data_table.data[id];

    instance.is_default = false;

    var row = $('.item_id_' + id).closest('tr');
    var cell_link = row.find('a[onclick*="toggle_default"]');

    cell_link.text(mllp.flag_label(false));
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
