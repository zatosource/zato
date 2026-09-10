

// Dashboard kit - the run summary, the fact rows of one run and the folded ledger of what it saw.

(function() {
    var kit = $.fn.zato.dashboard_kit;
    kit.runSummary = {};

    kit.runSummary.config = {

        // The ledger's columns, in reading order.
        ledgerColumns: ['Name', 'Size', 'Modified', 'Decision', 'Reason', 'Duration'],

        // What a cell with nothing to say reads as.
        emptyCell: '-',

        // What separates the decisions a filter chip stands for, on the chip's data attribute.
        decisionSeparator: ',',

        foldLabel: '{count} more',
        unfoldLabel: 'Fewer',

        // How many entries stay above the fold.
        foldAfter: 5,

        loadingLabel: 'Loading',
        emptyLabel: 'No entries',
        overflowLabel: '.. and {count} more',

        // The decisions listed above the fold whatever their place in the ledger.
        leadDecisions: {'failed': true, 'quarantined': true},

        tracebackLabel: 'Traceback',

        variantClasses: {
            'light': 'dashboard-run-summary-light',
            'dark': 'dashboard-run-summary-dark'
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    // The filter chips of {key, label, count, tone, decisions} as one fact's value, each narrows the ledger
    // down to the entries decided its way, a second click on the same chip lets the whole ledger back.
    kit.runSummary.filterChipsHTML = function(chips) {
        var config = kit.runSummary.config;

        var out = '<span class="dashboard-run-filters">';

        for (var chipIndex = 0; chipIndex < chips.length; chipIndex++) {
            var chip = chips[chipIndex];
            var decisions = chip.decisions.join(config.decisionSeparator);

            out += '<span class="detail-tag dashboard-chip ' + kit.chips.tone_classes[chip.tone] +
                ' dashboard-run-filter-chip" data-chip-key="' + kit._esc_html(chip.key) + '" ' +
                'data-decisions="' + kit._esc_html(decisions) + '">' +
                '<span class="dashboard-chip-value">' + kit._esc_html(String(chip.count)) + '</span> ' +
                kit._esc_html(chip.label) + '</span>';
        }

        out += '</span>';

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The entries with the lead decisions first, then the rest in their order.
    kit.runSummary.leadFirst = function(entries) {
        var config = kit.runSummary.config;

        var lead = [];
        var rest = [];

        for (var entryIndex = 0; entryIndex < entries.length; entryIndex++) {
            var entry = entries[entryIndex];

            if (config.leadDecisions[entry.decision] === true) {
                lead.push(entry);
            }
            else {
                rest.push(entry);
            }
        }

        return lead.concat(rest);
    };

    // ////////////////////////////////////////////////////////////////////////

    // A cell's text, or the empty cell when there is none.
    kit.runSummary.cellHTML = function(text) {
        var config = kit.runSummary.config;

        if (text === '') {
            return config.emptyCell;
        }

        return kit._esc_html(text);
    };

    // ////////////////////////////////////////////////////////////////////////

    // One ledger row of {name, sizeText, modifiedHTML, decision, decisionLabel, decisionTone, reason,
    // reasonLabel, durationText, linkURL}, an empty linkURL renders the name as text.
    kit.runSummary.ledgerRowHTML = function(entry, isHidden) {
        var out = '<tr class="dashboard-run-ledger-row" data-decision="' + kit._esc_html(entry.decision) + '"';

        if (isHidden) {
            out += ' hidden data-folded="1"';
        }

        out += '>';

        var nameHTML = kit._esc_html(entry.name);

        if (entry.linkURL !== '') {
            nameHTML = '<a href="' + kit._esc_html(entry.linkURL) + '" class="dashboard-run-ledger-link">' +
                nameHTML + '</a>';
        }

        var decisionChip = kit.chips.render_one({key: 'decision', label: '', value: entry.decision,
            text: entry.decisionLabel, tone: entry.decisionTone});

        out += '<td class="dashboard-run-ledger-name">' + nameHTML + '</td>';
        out += '<td class="dashboard-run-ledger-size">' + kit._esc_html(entry.sizeText) + '</td>';
        out += '<td class="dashboard-run-ledger-modified">' + entry.modifiedHTML + '</td>';
        out += '<td class="dashboard-run-ledger-decision">' + decisionChip + '</td>';
        out += '<td class="dashboard-run-ledger-reason">' + kit.runSummary.cellHTML(entry.reasonLabel) + '</td>';
        out += '<td class="dashboard-run-ledger-duration">' + kit.runSummary.cellHTML(entry.durationText) + '</td>';
        out += '</tr>';

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The fold badge under the ledger.
    kit.runSummary.foldHTML = function(entryCount, isUnfolded) {
        var config = kit.runSummary.config;

        var foldLabel = config.foldLabel.replace('{count}', kit.format_number_full(entryCount - config.foldAfter));
        var foldText = foldLabel;

        if (isUnfolded) {
            foldText = config.unfoldLabel;
        }

        var out = '<div class="dashboard-run-ledger-fold"><span class="dashboard-panel-action-badge ' +
            'dashboard-run-ledger-fold-toggle" data-unfolded="' + (isUnfolded ? '1' : '0') + '" ' +
            'data-fold-label="' + kit._esc_html(foldLabel) + '">' + foldText + '</span></div>';

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The ledger table with its fold, overflow is how many entries the run saw past what it kept.
    kit.runSummary.ledgerHTML = function(entries, overflow, isUnfolded) {
        var config = kit.runSummary.config;

        if (entries.length === 0) {
            return '<div class="dashboard-run-ledger-empty">' + config.emptyLabel + '</div>';
        }

        var ordered = kit.runSummary.leadFirst(entries);

        var out = '<table class="dashboard-run-ledger"><thead><tr>';

        for (var columnIndex = 0; columnIndex < config.ledgerColumns.length; columnIndex++) {
            out += '<th>' + config.ledgerColumns[columnIndex] + '</th>';
        }

        out += '</tr></thead><tbody>';

        for (var entryIndex = 0; entryIndex < ordered.length; entryIndex++) {
            var isHidden = !isUnfolded && entryIndex >= config.foldAfter;
            out += kit.runSummary.ledgerRowHTML(ordered[entryIndex], isHidden);
        }

        out += '</tbody></table>';

        if (overflow > 0) {
            var overflowText = config.overflowLabel.replace('{count}', kit.format_number_full(overflow));
            out += '<div class="dashboard-run-ledger-overflow">' + overflowText + '</div>';
        }

        if (ordered.length > config.foldAfter) {
            out += kit.runSummary.foldHTML(ordered.length, isUnfolded);
        }

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // The frame of a summary of {variant, foldKey}.
    kit.runSummary.frameHTML = function(summary, innerHTML) {
        var config = kit.runSummary.config;

        var out = '<div class="dashboard-run-summary ' + config.variantClasses[summary.variant] + '" ' +
            'data-fold-key="' + kit._esc_html(summary.foldKey) + '">';

        out += innerHTML;
        out += '</div>';

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    // A summary of {factsHTML, variant, foldKey}, the ledger arrives later through fillLedger.
    kit.runSummary.render = function(summary) {
        var config = kit.runSummary.config;

        var inner = summary.factsHTML;
        inner += '<div class="dashboard-run-ledger-host"><div class="dashboard-run-ledger-loading">' +
            config.loadingLabel + '</div></div>';

        var out = kit.runSummary.frameHTML(summary, inner);

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    kit.runSummary.fillLedger = function($summary, entries, overflow) {
        var foldKey = $summary.attr('data-fold-key');
        var isUnfolded = kit.runSummary.folds.isUnfolded(foldKey);

        var ledgerHTML = kit.runSummary.ledgerHTML(entries, overflow, isUnfolded);
        $summary.find('.dashboard-run-ledger-host').html(ledgerHTML);
    };

    // ////////////////////////////////////////////////////////////////////////

    // A summary of {factsHTML, variant, foldKey} for a run without a ledger, the traceback arrives through fillError.
    kit.runSummary.renderError = function(summary) {
        var inner = summary.factsHTML;
        inner += '<div class="dashboard-run-traceback-host"></div>';

        var out = kit.runSummary.frameHTML(summary, inner);

        return out;
    };

    // ////////////////////////////////////////////////////////////////////////

    kit.runSummary.fillError = function($summary, traceback) {
        var config = kit.runSummary.config;

        if (traceback === '') {
            return;
        }

        var foldKey = $summary.attr('data-fold-key');
        var isUnfolded = kit.runSummary.folds.isUnfolded(foldKey);

        var out = '<div class="dashboard-run-ledger-fold"><span class="dashboard-panel-action-badge ' +
            'dashboard-run-traceback-toggle" data-unfolded="' + (isUnfolded ? '1' : '0') + '">' +
            config.tracebackLabel + '</span></div>';

        out += '<pre class="dashboard-run-traceback"';

        if (!isUnfolded) {
            out += ' hidden';
        }

        out += '>' + kit._esc_html(traceback) + '</pre>';

        $summary.find('.dashboard-run-traceback-host').html(out);
    };

    // ////////////////////////////////////////////////////////////////////////

    // The unfolded summaries, remembered in local storage under their fold keys.
    kit.runSummary.folds = {

        storageKey: 'audit-log.file-outgoing.folds',

        read: function() {
            var raw = window.localStorage.getItem(kit.runSummary.folds.storageKey);

            if (raw === null) {
                return {};
            }

            return JSON.parse(raw);
        },

        isUnfolded: function(foldKey) {
            var folds = kit.runSummary.folds.read();
            return folds[foldKey] === true;
        },

        set: function(foldKey, isUnfolded) {
            var folds = kit.runSummary.folds.read();
            folds[foldKey] = isUnfolded;
            window.localStorage.setItem(kit.runSummary.folds.storageKey, JSON.stringify(folds));
        }
    };

    // ////////////////////////////////////////////////////////////////////////

    $(document).on('click', '.dashboard-run-traceback-toggle', function(event) {
        event.stopPropagation();

        var $toggle = $(this);
        var $summary = $toggle.closest('.dashboard-run-summary');
        var nowUnfolded = $toggle.attr('data-unfolded') !== '1';

        $summary.find('.dashboard-run-traceback').prop('hidden', !nowUnfolded);
        $toggle.attr('data-unfolded', nowUnfolded ? '1' : '0');

        kit.runSummary.folds.set($summary.attr('data-fold-key'), nowUnfolded);
    });

    // ////////////////////////////////////////////////////////////////////////

    $(document).on('click', '.dashboard-run-ledger-fold-toggle', function(event) {
        event.stopPropagation();

        var config = kit.runSummary.config;
        var $toggle = $(this);
        var $summary = $toggle.closest('.dashboard-run-summary');
        var isUnfolded = $toggle.attr('data-unfolded') === '1';

        var nowUnfolded = !isUnfolded;

        $summary.find('.dashboard-run-ledger-row[data-folded="1"]').prop('hidden', !nowUnfolded);
        $toggle.attr('data-unfolded', nowUnfolded ? '1' : '0');
        $toggle.text(nowUnfolded ? config.unfoldLabel : $toggle.attr('data-fold-label'));

        kit.runSummary.folds.set($summary.attr('data-fold-key'), nowUnfolded);
    });

    // ////////////////////////////////////////////////////////////////////////

    // The ledger back to how the fold leaves it, no chip narrowing it down.
    kit.runSummary.clearFilter = function($summary) {
        var $toggle = $summary.find('.dashboard-run-ledger-fold-toggle');
        var isUnfolded = $toggle.attr('data-unfolded') === '1';

        $summary.find('.dashboard-run-filter-chip').removeClass('dashboard-run-filter-chip-active');

        $summary.find('.dashboard-run-ledger-row').each(function() {
            var $row = $(this);
            var isFolded = $row.attr('data-folded') === '1';
            $row.prop('hidden', isFolded && !isUnfolded);
        });

        $summary.find('.dashboard-run-ledger-fold').prop('hidden', false);
    };

    // ////////////////////////////////////////////////////////////////////////

    // A filter chip narrows the ledger down to the entries decided its way, every one of them shown
    // whatever the fold, and the chip already narrowing it lets the whole ledger back.
    $(document).on('click', '.dashboard-run-filter-chip', function(event) {
        event.stopPropagation();

        var config = kit.runSummary.config;
        var $chip = $(this);
        var $summary = $chip.closest('.dashboard-run-summary');

        if ($chip.hasClass('dashboard-run-filter-chip-active')) {
            kit.runSummary.clearFilter($summary);
            return;
        }

        var wanted = {};
        var decisions = $chip.attr('data-decisions').split(config.decisionSeparator);

        for (var decisionIndex = 0; decisionIndex < decisions.length; decisionIndex++) {
            wanted[decisions[decisionIndex]] = true;
        }

        $summary.find('.dashboard-run-filter-chip').removeClass('dashboard-run-filter-chip-active');
        $chip.addClass('dashboard-run-filter-chip-active');

        $summary.find('.dashboard-run-ledger-row').each(function() {
            var $row = $(this);
            $row.prop('hidden', wanted[$row.attr('data-decision')] !== true);
        });

        $summary.find('.dashboard-run-ledger-fold').prop('hidden', true);
    });
})();
