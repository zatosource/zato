

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

        // A tab is a badge like every other thing that can be clicked on a dark panel, and the
        // one standing open is the one wearing the badge's own open state
        for (var tab_index = 0; tab_index < tabs.length; tab_index++) {
            var tab_class = tab_index === 0 ? ' dashboard-panel-action-badge-active' : '';

            html += '<span class="dashboard-panel-action-badge dashboard-panel-action-badge-dark ' +
                'dashboard-payload-tab' + tab_class + '" data-tab-index="' + tab_index + '">';

            // A tab whose label brings its own markup wears it as it is - one that is
            // a plain word is escaped like any other text
            if (tabs[tab_index].label_html === undefined) {
                html += kit._esc_html(tabs[tab_index].label);
            }
            else {
                html += tabs[tab_index].label_html;
            }

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

            // A tab holding rows rather than words is read as a table
            if (tab.table !== undefined) {
                html += '<div class="dashboard-payload-text dashboard-payload-table-holder" data-tab-index="' +
                    pane_index + '"' + hidden_attr + '>';
                html += kit.payload_panel._table_html(tab.table);
                html += '</div>';
                continue;
            }

            html += '<pre class="dashboard-payload-text" data-tab-index="' + pane_index + '"' + hidden_attr + '>';

            // A tab whose text is already here shows it, and one whose text is still
            // to be fetched shows nothing until its turn comes. SQL stands escaped
            // for now - its colours come from the server once the frame is up.
            if (tab.text === undefined) {
                html += '';
            }
            else if (kit._sql_starter_pattern.test(tab.text.trim())) {
                html += '<span class="syntax-monokai">' + kit._esc_html(tab.text) + '</span>';
            }
            else {
                html += kit.syntax_highlight(tab.text);
            }

            html += '</pre>';
        }

        html += '</div>';

        return html;
    };

    /* Rows out of a database drawn as the table they are - a header of column
       names and one line per row. */
    kit.payload_panel._table_html = function(table) {
        var html = '<table class="dashboard-payload-table"><thead><tr>';

        for (var column_index = 0; column_index < table.columns.length; column_index++) {
            html += '<th>' + kit._esc_html(table.columns[column_index]) + '</th>';
        }

        html += '</tr></thead><tbody>';

        for (var row_index = 0; row_index < table.rows.length; row_index++) {
            html += '<tr>';

            var row = table.rows[row_index];

            for (var cell_index = 0; cell_index < row.length; cell_index++) {
                html += '<td>' + kit._esc_html(String(row[cell_index])) + '</td>';
            }

            html += '</tr>';
        }

        html += '</tbody></table>';

        return html;
    };

    /* Puts one text into one pane - most kinds are coloured right here, SQL is sent
       to the server's pygments, the escaped text standing in until the colours land. */
    kit.payload_panel._show_text = function($pane, text) {
        if (kit._sql_starter_pattern.test(text.trim())) {
            $pane.html('<span class="syntax-monokai">' + kit._esc_html(text) + '</span>');

            // The colours are for this very text - a pane brought to another
            // message in the meantime keeps that message's words instead
            var token = $pane.data('payload_token');

            kit._highlight_remote(text, 'sql', function(html) {
                if ($pane.data('payload_token') !== token) {
                    return;
                }

                $pane.html('<span class="syntax-monokai">' + html + '</span>');
            });

            return;
        }

        $pane.html(kit.syntax_highlight(text));
    };

    /* Asks the server for the colours of every SQL pane of a freshly built frame -
       the panes already stand with their text escaped, so nothing moves meanwhile. */
    kit.payload_panel._color_sql = function($panel) {
        var tabs = $panel.data('payload_tabs');

        $panel.find('.dashboard-payload-text').each(function() {
            var $pane = $(this);
            var tab = tabs[parseInt($pane.attr('data-tab-index'), 10)];

            if (tab.text !== undefined && kit._sql_starter_pattern.test(tab.text.trim())) {
                kit.payload_panel._show_text($pane, tab.text);
            }
        });
    };

    /* A panel whose every tab already has its text. */
    kit.payload_panel.render = function($host, tabs) {
        $host.html(kit.payload_panel._html(tabs));

        var $panel = $host.find('.dashboard-payload');
        $panel.data('payload_tabs', tabs);

        kit.payload_panel._color_sql($panel);
    };

    /* A panel whose tabs fetch their own text. `fetch(tab, done)` calls `done(text)`
       when the text of that one tab has arrived, and is called once per tab at most.
       `open_index` names the tab the panel opens on, the first one when left unsaid. */
    kit.payload_panel.lazy = function($host, tabs, fetch, open_index) {
        $host.html(kit.payload_panel._html(tabs));

        var $panel = $host.find('.dashboard-payload');
        $panel.data('payload_tabs', tabs);
        $panel.data('payload_fetch', fetch);

        kit.payload_panel._color_sql($panel);

        if (open_index === undefined) {
            open_index = 0;
        }

        // The tab that is open is the one worth having right away.
        kit.payload_panel._activate($panel, open_index);
        kit.payload_panel._fill($panel, open_index);
    };

    /* The panel brought to another message. A frame whose tabs are these very tabs is kept
       where it stands and only its text is asked for again, so reading down a list swaps
       words rather than tearing the frame down and putting it back up. A caller that says
       which tab is to be open is obeyed, one that says nothing leaves the open tab alone. */
    kit.payload_panel.swap = function($host, tabs, fetch, open_index) {
        var $panel = $host.find('.dashboard-payload');

        // A message read in other tabs than these needs a frame of its own.
        if (!kit.payload_panel._same_tabs($panel, tabs)) {
            kit.payload_panel.lazy($host, tabs, fetch, open_index);
            return;
        }

        $panel.data('payload_tabs', tabs);
        $panel.data('payload_fetch', fetch);

        // Every pane is owed the text of the new message, and the tab standing open is
        // the one worth having right away.
        $panel.find('.dashboard-payload-text').data('payload_loaded', false);

        if (open_index === undefined) {
            open_index = $panel.find('.dashboard-payload-tab.dashboard-panel-action-badge-active')
                .attr('data-tab-index');
        }
        else {
            kit.payload_panel._activate($panel, open_index);
        }

        kit.payload_panel._fill($panel, open_index);
    };

    /* Puts one tab in front - its badge lit and its pane the one on the screen. */
    kit.payload_panel._activate = function($panel, tab_index) {
        $panel.find('.dashboard-payload-tab').removeClass('dashboard-panel-action-badge-active');
        $panel.find('.dashboard-payload-tab[data-tab-index="' + tab_index + '"]')
            .addClass('dashboard-panel-action-badge-active');

        $panel.find('.dashboard-payload-text').attr('hidden', 'hidden');
        $panel.find('.dashboard-payload-text[data-tab-index="' + tab_index + '"]').removeAttr('hidden');
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
            kit.payload_panel._show_text($pane, text);
        });
    };

    $(document).on('click', '.dashboard-payload-tab', function() {
        var $tab = $(this);
        var $panel = $tab.closest('.dashboard-payload');
        var tab_index = $tab.attr('data-tab-index');

        kit.payload_panel._activate($panel, tab_index);
        kit.payload_panel._fill($panel, tab_index);
    });

    $(document).on('click', '.dashboard-payload-copy', function() {
        var $panel = $(this).closest('.dashboard-payload');
        var $pane = $panel.find('.dashboard-payload-text:not([hidden])');

        var tabs = $panel.data('payload_tabs');
        var tab = tabs[parseInt($pane.attr('data-tab-index'), 10)];

        var text;

        // A table copies as its rows, tab-separated, header first - text copies as it stands
        if (tab.table === undefined) {
            text = $pane.text();
        }
        else {
            var lines = [tab.table.columns.join('\t')];

            for (var row_index = 0; row_index < tab.table.rows.length; row_index++) {
                lines.push(tab.table.rows[row_index].join('\t'));
            }

            text = lines.join('\n');
        }

        kit.copy_to_clipboard(this, text);
    });
})();
