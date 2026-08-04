

/* Dashboard kit - the payload panel.
   One piece of text in a dark frame, coloured by the kit's own highlighter, with a tab per
   way of reading it and a button that copies whichever one is open. A tab's text may be
   there from the start or may be fetched the first time the tab is opened. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.payload_panel = {};

    kit.payload_panel.config = {
        copy_label: 'Copy',

        // How long a pane waits for its text before it says it is waiting - a body read
        // from the server nearby usually arrives first, and then nothing is announced at all
        spinner_delay_ms: 150
    };

    kit.payload_panel.spinner_html = function() {
        var html = '<div class="dashboard-payload-loading">' + kit.spinner_label_html() + '</div>';
        return html;
    };

    /* The frame itself - the tab bar, the Copy button and one text pane per tab,
       with the first tab open. */
    kit.payload_panel._html = function(tabs) {
        var config = kit.payload_panel.config;

        var html = '<div class="dashboard-payload">';
        html += '<div class="dashboard-payload-bar">';

        for (var tab_index = 0; tab_index < tabs.length; tab_index++) {
            var tab_class = tab_index === 0 ? ' dashboard-payload-tab-active' : '';

            html += '<span class="dashboard-payload-tab' + tab_class + '" data-tab-index="' + tab_index + '">';
            html += kit._esc_html(tabs[tab_index].label);
            html += '</span>';
        }

        // The panel is dark, so its actions wear the same badge every action on a dark
        // panel wears elsewhere on the dashboard
        html += '<span class="dashboard-payload-actions">';
        html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
            'dashboard-payload-copy">' + config.copy_label + '</span>';
        html += '</span>';
        html += '</div>';

        for (var pane_index = 0; pane_index < tabs.length; pane_index++) {
            var hidden_attr = pane_index === 0 ? '' : ' hidden';
            var tab = tabs[pane_index];

            html += '<pre class="dashboard-payload-text" data-tab-index="' + pane_index + '"' + hidden_attr + '>';

            // A tab whose text is already here shows it, and one whose text is still
            // to be fetched shows nothing until its turn comes.
            if (tab.text === undefined) {
                html += '';
            }
            else {
                html += kit.syntax_highlight(tab.text);
            }

            html += '</pre>';
        }

        html += '</div>';

        return html;
    };

    /* A panel whose every tab already has its text. */
    kit.payload_panel.render = function($host, tabs) {
        $host.html(kit.payload_panel._html(tabs));
        $host.find('.dashboard-payload').data('payload_tabs', tabs);
    };

    /* A panel whose tabs fetch their own text. `fetch(tab, done)` calls `done(text)`
       when the text of that one tab has arrived, and is called once per tab at most. */
    kit.payload_panel.lazy = function($host, tabs, fetch) {
        $host.html(kit.payload_panel._html(tabs));

        var $panel = $host.find('.dashboard-payload');
        $panel.data('payload_tabs', tabs);
        $panel.data('payload_fetch', fetch);

        // The tab that is already open is the one worth having right away.
        kit.payload_panel._fill($panel, 0);
    };

    /* The panel brought to another message. A frame whose tabs are these very tabs is kept
       where it stands and only its text is asked for again, so reading down a list swaps
       words rather than tearing the frame down and putting it back up. */
    kit.payload_panel.swap = function($host, tabs, fetch) {
        var $panel = $host.find('.dashboard-payload');

        // A message read in other tabs than these needs a frame of its own.
        if (!kit.payload_panel._same_tabs($panel, tabs)) {
            kit.payload_panel.lazy($host, tabs, fetch);
            return;
        }

        $panel.data('payload_tabs', tabs);
        $panel.data('payload_fetch', fetch);

        // Every pane is owed the text of the new message, and the tab standing open is
        // the one worth having right away.
        $panel.find('.dashboard-payload-text').data('payload_loaded', false);

        var open_index = $panel.find('.dashboard-payload-tab-active').attr('data-tab-index');
        kit.payload_panel._fill($panel, open_index);
    };

    /* Whether a panel already carries this very set of tabs, which is what tells a frame
       that can be kept from one that has to be built again. */
    kit.payload_panel._same_tabs = function($panel, tabs) {

        // Nothing has been built here yet.
        if (!$panel.length) {
            return false;
        }

        var current = $panel.data('payload_tabs');

        if (current.length !== tabs.length) {
            return false;
        }

        for (var tab_index = 0; tab_index < tabs.length; tab_index++) {
            if (current[tab_index].label !== tabs[tab_index].label) {
                return false;
            }
        }

        return true;
    };

    /* Puts the text of one tab in place, asking for it if this is its first showing. */
    kit.payload_panel._fill = function($panel, tab_index) {
        var config = kit.payload_panel.config;
        var $pane = $panel.find('.dashboard-payload-text[data-tab-index="' + tab_index + '"]');

        // A pane filled once keeps what it was given - the payload of an event does not change.
        if ($pane.data('payload_loaded')) {
            return;
        }

        var fetch = $panel.data('payload_fetch');

        // A panel rendered with its text in hand has nothing to fetch.
        if (fetch === undefined) {
            return;
        }

        var tabs = $panel.data('payload_tabs');
        $pane.data('payload_loaded', true);

        // Each request a pane makes is numbered, so a body arriving after the pane has been
        // brought to another message is dropped rather than read as that message.
        var token = $pane.data('payload_token');

        if (token === undefined) {
            token = 0;
        }

        token = token + 1;
        $pane.data('payload_token', token);

        // Whatever the pane is holding stays there while the next text is on its way, and
        // the wait is only announced once it is long enough to be worth announcing.
        var spinner_timer = setTimeout(function() {
            if ($pane.data('payload_token') !== token) {
                return;
            }

            $pane.html(kit.payload_panel.spinner_html());
        }, config.spinner_delay_ms);

        fetch(tabs[tab_index], function(text) {
            if ($pane.data('payload_token') !== token) {
                return;
            }

            clearTimeout(spinner_timer);
            $pane.html(kit.syntax_highlight(text));
        });
    };

    $(document).on('click', '.dashboard-payload-tab', function() {
        var $tab = $(this);
        var $panel = $tab.closest('.dashboard-payload');
        var tab_index = $tab.attr('data-tab-index');

        $panel.find('.dashboard-payload-tab').removeClass('dashboard-payload-tab-active');
        $tab.addClass('dashboard-payload-tab-active');

        $panel.find('.dashboard-payload-text').attr('hidden', 'hidden');
        $panel.find('.dashboard-payload-text[data-tab-index="' + tab_index + '"]').removeAttr('hidden');

        kit.payload_panel._fill($panel, tab_index);
    });

    $(document).on('click', '.dashboard-payload-copy', function() {
        var $panel = $(this).closest('.dashboard-payload');
        var text = $panel.find('.dashboard-payload-text:not([hidden])').text();

        kit.copy_to_clipboard(this, text);
    });
})();
