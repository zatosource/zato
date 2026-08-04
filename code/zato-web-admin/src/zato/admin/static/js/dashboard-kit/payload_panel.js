

/* Dashboard kit - the payload panel.
   One piece of text in a dark frame, with a tab per way of reading it and a button that
   copies whichever one is open. A tab's text may be there from the start or may be fetched
   the first time the tab is opened. */



(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.payload_panel = {};

    kit.payload_panel.config = {
        copy_label: 'Copy',
        loading_label: 'Loading',
        spinner_url: '/static/gfx/spinner.svg'
    };

    kit.payload_panel.spinner_html = function() {
        var config = kit.payload_panel.config;

        var html = '<div class="dashboard-payload-loading">';
        html += '<img src="' + config.spinner_url + '" class="detail-spinner"> ' + config.loading_label;
        html += '</div>';

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

        html += '<span class="dashboard-payload-actions">';
        html += '<input type="button" class="dashboard-payload-copy" value="' + config.copy_label + '">';
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
                html += kit._esc_html(tab.text);
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

    /* Puts the text of one tab in place, asking for it if this is its first showing. */
    kit.payload_panel._fill = function($panel, tab_index) {
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
        $pane.html(kit.payload_panel.spinner_html());

        fetch(tabs[tab_index], function(text) {
            $pane.text(text);
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
