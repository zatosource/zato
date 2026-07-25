'use strict';

// Rendering for the rulesets home: the list with status on every row,
// full-text matches shown as readable sentences with the hit highlighted,
// the recents strip, the saved view chips, and the side pane, which is
// the change feed until a row is selected and that ruleset's preview
// afterwards. Event handlers live in rulesets-actions.js, the right-click
// menu in rulesets-menu.js.

(function() {

var rulesetsView = {

    config: {
        // The list renders a capped window no matter how many rulesets
        // exist, the filter is the way in past the cap
        maxVisibleRows: 200,
        // A row shows at most this many matching sentences, the preview
        // shows the rest
        maxRowMatches: 3,
        // The preview shows at most this many rules and history entries
        maxPreviewRules: 6,
        maxPreviewEvents: 5,
        // Views stay few and named, a long view list wastes more time
        // than it saves
        maxSavedViews: 5,
        // A rename impact lists this many renamed rules, the count covers the rest
        maxRenamedRules: 6,

        // A ruleset name is dotted words, the same shape the server enforces
        rulesetNamePattern: /^\w+(\.\w+)*$/,

        // Where a ruleset opens into, each screen reads the parameter
        openUrls: {
            tables: '/tables/',
            editor: '/editor/',
            tests: '/tests/',
            versions: '/versions/',
            log: '/decision-log/',
            vocabulary: '/vocabulary/',
        },

        // Every history event type as the phrase the feed shows
        eventPhrases: {
            'definition.created': 'created this ruleset',
            'definition.renamed': 'renamed this ruleset',
            'definition.updated': 'updated this ruleset',
            'definition.archived': 'archived this ruleset',
            'version.created': 'stored a new version',
            'version.published': 'published a version',
            'version.restored': 'restored an earlier version',
            'review.commented': 'commented in a review',
            'state.changed': 'changed the state',
            'follow.changed': 'changed who follows it',
            'test.run': 'ran a test set',
            'rule.fired.daily': 'recorded daily rule counts',
            'advisory.run': 'ran the advisory checks',
            'decisions.spiked': 'saw a spike in decisions',
            'version.approved': 'approved a version',
            'approval.requested': 'requested an approval',
            'approval.gate.enabled': 'enabled the approval gate',
            'approval.gate.disabled': 'disabled the approval gate',
            'approval.self.changed': 'changed self-approval',
        },
    },

    // UI state
    query: '',
    view: 'all',
    selectedId: null,

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        this.renderRecents();
        this.renderSavedViews();
        this.renderList();
        this.renderSide();
        this.renderProblems();
        shared.initTips();
    },

// ////////////////////////////////////////////////////////////////////////

    // Timestamps come from the views as ISO strings, the screen shows
    // the readable date-and-minute part
    whenText: function(iso) {
        return iso.slice(0, 16).replace('T', ' ');
    },

// ////////////////////////////////////////////////////////////////////////

    markHtml: function(text) {
        if (this.query.trim() === '') { return shared.escape(text); }

        // The match is highlighted in place, case preserved
        var needle = this.query.trim().toLowerCase();
        var lower = text.toLowerCase();
        var out = '';
        var from = 0;
        var position = lower.indexOf(needle, from);

        while (position > -1) {
            out += shared.escape(text.slice(from, position));
            out += '<mark class="rulesets-mark">' + shared.escape(text.slice(position, position + needle.length)) + '</mark>';
            from = position + needle.length;
            position = lower.indexOf(needle, from);
        }
        out += shared.escape(text.slice(from));
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    statusHtml: function(ruleset) {
        var draft = rulesetsModel.draftVersion(ruleset);
        var out = '';

        if (ruleset.live_version !== null) {
            out += '<span class="rulesets-badge rulesets-badge-live" ' +
                'data-tippy-content="This version answers requests right now.">live v' + ruleset.live_version + '</span>';
        }
        if (draft !== null) {
            out += '<span class="rulesets-badge rulesets-badge-draft" ' +
                'data-tippy-content="A draft is in progress, the live version keeps answering until it is published.">draft v' + draft + '</span>';
            out += '<button class="button-mini rulesets-publish" ' +
                'onclick="event.stopPropagation(); rulesetsView.openPublishPanel(' + ruleset.id + ', this)" ' +
                'data-tippy-content="Publish draft v' + draft +
                ': a confirmation first, a snapshot is taken and the new version starts answering.">publish</button>';
        }
        return out;
    },

    starHtml: function(ruleset) {
        var followed = rulesetsModel.isFollowed(ruleset.id);
        var stateClass = followed ? ' rulesets-star-on' : '';
        var hint = followed
            ? 'You follow this ruleset, its changes lead the feed. Click to unfollow.'
            : 'Not followed. Click to follow, its changes will lead the feed.';

        var out = '<span class="rulesets-star' + stateClass + '" ' +
            'onclick="event.stopPropagation(); rulesetsView.toggleFollow(' + ruleset.id + ')" ' +
            'data-tippy-content="' + hint + '">' + shared.icon('star', 13) + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    renderList: function() {
        var self = this;
        var entries = rulesetsModel.filtered(this.view, this.query);
        var cap = this.config.maxVisibleRows;
        var html = '';
        var shown = 0;

        entries.forEach(function(entry) {
            if (shown >= cap) { return; }
            shown += 1;

            var ruleset = entry.ruleset;
            var selected = ruleset.id === self.selectedId ? ' rulesets-row-selected' : '';

            html += '<div class="rulesets-row' + selected + '" data-id="' + ruleset.id + '" ' +
                'onclick="rulesetsView.select(' + ruleset.id + ')" ' +
                'ondblclick="rulesetsView.open(' + ruleset.id + ')">' +
                '<div class="rulesets-row-main">' +
                '<div class="rulesets-row-name">' + self.starHtml(ruleset) +
                '<a class="rulesets-open-link" href="' + self.config.openUrls.tables + '?ruleset=' + ruleset.id + '" ' +
                    'onclick="return rulesetsView.openFromLink(event, ' + ruleset.id + ')">' +
                    self.markHtml(ruleset.name) + '</a>' +
                self.statusHtml(ruleset) + '</div>' +
                self.hitsHtml(entry.hits) +
                '</div>' +
                '<div class="rulesets-row-columns">' +
                '<span class="rulesets-cell">v' + ruleset.current_version + ' stored</span>' +
                '<span class="rulesets-cell rulesets-cell-change">updated ' + self.whenText(ruleset.updated_at) + '</span>' +
                '</div>' +
                '</div>';
        });

        if (html === '') {
            html = '<div class="rulesets-empty">Nothing matches. The search reads rule text too, try a word from inside a rule, like "score".</div>';
        }
        if (entries.length > shown) {
            html += '<div class="rulesets-more">Showing the first ' + shown + ' of ' + entries.length +
                ' matching rulesets, the search above narrows this down.</div>';
        }

        document.getElementById('rulesets-count').textContent = entries.length + ' rulesets';
        document.getElementById('rulesets-list').innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    // One full-text hit: the matching sentence itself, readable, with
    // the hit marked at the exact place the search reported
    hitHtml: function(hit) {
        var line = hit.line;
        var out = '<div class="rulesets-match">' +
            shared.escape(line.slice(0, hit.match_start)) +
            '<mark class="rulesets-mark">' + shared.escape(line.slice(hit.match_start, hit.match_end)) + '</mark>' +
            shared.escape(line.slice(hit.match_end)) +
            '<span class="rulesets-match-where">' + shared.escape(hit.rule) + '</span></div>';
        return out;
    },

    hitsHtml: function(hits) {
        var self = this;
        var out = '';
        hits.slice(0, this.config.maxRowMatches).forEach(function(hit) {
            out += self.hitHtml(hit);
        });
        if (hits.length > this.config.maxRowMatches) {
            out += '<div class="rulesets-match-overflow">and ' + (hits.length - this.config.maxRowMatches) +
                ' more matching lines</div>';
        }
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    renderSide: function() {
        var self = this;
        var pane = document.getElementById('rulesets-side');

        if (this.selectedId === null) {
            pane.innerHTML = this.feedHtml();
            shared.initTips();
            return;
        }

        rulesetsModel.preview(this.selectedId, function(preview) {
            pane.innerHTML = self.previewHtml(preview);
            shared.initTips();

            // Opening a preview counts as a visit, the strip follows suit
            rulesetsModel.loadRecents(function() { self.renderRecents(); });
        });
    },

    eventLine: function(entry) {
        var out = this.config.eventPhrases[entry.event_type];
        if (entry.version !== null) { out += ', v' + entry.version; }
        return out;
    },

    feedHtml: function() {
        var self = this;
        var html = '<div class="test-grid-title">Since you were last here</div>';

        if (rulesetsModel.feed.length === 0) {
            html += '<div class="rulesets-preview-note">Nothing new on the rulesets you follow. ' +
                'The star on a row starts following it.</div>';
            return html;
        }

        rulesetsModel.feed.forEach(function(entry) {
            var ruleset = rulesetsModel.byId(entry.definition_id);
            var name = ruleset === undefined ? 'ruleset ' + entry.definition_id : ruleset.name;

            html += '<div class="rulesets-feed-entry">' +
                '<div class="rulesets-feed-head">' + shared.escape(entry.actor) + ', ' + self.whenText(entry.created_at) +
                ' <span class="rulesets-feed-ruleset">' + shared.escape(name) + '</span></div>' +
                '<div class="rulesets-feed-what">' + self.eventLine(entry) + '</div>' +
                '</div>';
        });
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    // The preview answers "do I need to open it" without opening it
    previewHtml: function(preview) {
        var self = this;
        var ruleset = preview.definition;
        var draft = rulesetsModel.draftVersion(ruleset);

        var html = '<div class="test-grid-title">' + shared.escape(ruleset.name) +
            '<button class="button-mini rulesets-rename" ' +
            'onclick="rulesetsView.openRenamePanel(' + ruleset.id + ', this)" ' +
            'data-tippy-content="Rename the ruleset: the impact first, including how many calls its ' +
            'current name has served.">rename</button></div>';

        var statusValue = (ruleset.live_version === null ? 'never published' : 'live v' + ruleset.live_version) +
            (draft === null ? '' : ', draft v' + draft + ' in progress');
        if (draft !== null) {
            statusValue += ' <button class="button-mini rulesets-publish" ' +
                'onclick="rulesetsView.openPublishPanel(' + ruleset.id + ', this)" ' +
                'data-tippy-content="Publish draft v' + draft +
                ': a confirmation first, a snapshot is taken and the new version starts answering.">publish</button>';
        }

        var followValue = preview.is_following
            ? 'yes, its changes lead the feed'
            : 'no, the star on its row starts following it';

        html += '<table class="test-grid"><tbody>';
        html += '<tr><td class="test-label-cell">status</td><td class="test-value-cell log-value-readonly">' +
            statusValue + '</td></tr>';
        html += '<tr><td class="test-label-cell">created</td><td class="test-value-cell log-value-readonly">' +
            this.whenText(ruleset.created_at) + '</td></tr>';
        html += '<tr><td class="test-label-cell">last change</td><td class="test-value-cell log-value-readonly">' +
            this.whenText(ruleset.updated_at) + '</td></tr>';
        html += '<tr><td class="test-label-cell">followed</td><td class="test-value-cell log-value-readonly">' +
            followValue + '</td></tr>';
        html += '</tbody></table>';

        html += '<div class="test-grid-title">Open</div>' +
            '<div class="rulesets-preview-links">' +
            this.previewLinkHtml(ruleset.id, 'tables', 'Decision table') +
            this.previewLinkHtml(ruleset.id, 'editor', 'Sentence rules') +
            this.previewLinkHtml(ruleset.id, 'tests', 'Tests and A/B') +
            this.previewLinkHtml(ruleset.id, 'versions', 'Versions') +
            this.previewLinkHtml(ruleset.id, 'log', 'Decision log') +
            this.previewLinkHtml(ruleset.id, 'vocabulary', 'Vocabulary') +
            '</div>';

        // The rendered rules are the sentences a person reads, the first
        // few are enough to recognize the ruleset
        if (preview.rendered !== null) {
            var lines = preview.rendered.split('\n').filter(function(line) { return line.trim() !== ''; });
            html += '<div class="test-grid-title">A few of its rules</div>';
            lines.slice(0, this.config.maxPreviewRules).forEach(function(line) {
                html += '<div class="rulesets-match">' + shared.escape(line) + '</div>';
            });
        }

        if (preview.events.length > 0) {
            html += '<div class="test-grid-title">Recent history</div>';
            preview.events.slice(0, this.config.maxPreviewEvents).forEach(function(entry) {
                html += '<div class="rulesets-feed-entry">' +
                    '<div class="rulesets-feed-head">' + shared.escape(entry.actor) + ', ' +
                        self.whenText(entry.created_at) + '</div>' +
                    '<div class="rulesets-feed-what">' + self.eventLine(entry) + '</div>' +
                    '</div>';
            });
        }

        return html;
    },

    previewLinkHtml: function(id, screen, label) {
        var out = '<a class="rulesets-preview-link" href="' + this.config.openUrls[screen] + '?ruleset=' + id + '">' +
            label + '</a>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // The recents strip: what was opened before, one click back into it
    renderRecents: function() {
        var strip = document.getElementById('rulesets-recents');
        var html = '';

        rulesetsModel.recents.forEach(function(recent) {
            var ruleset = rulesetsModel.byId(recent.definition_id);

            // A recent visit may point past the list's window, the strip
            // only shows what the list can select
            if (ruleset === undefined) { return; }

            html += '<button class="button-ghost rulesets-recent-chip" ' +
                'onclick="rulesetsView.pickRecent(' + ruleset.id + ')" ' +
                'data-tippy-content="Selects it in the list, double-click a row or press Enter to open it again.">' +
                shared.escape(ruleset.name) + '</button>';
        });

        if (html === '') {
            strip.innerHTML = '';
            strip.style.display = 'none';
            return;
        }

        strip.style.display = 'flex';
        strip.innerHTML = '<span class="rulesets-recents-label">Recently opened</span>' + html;
    },

// ////////////////////////////////////////////////////////////////////////

    // Saved views render as chips next to the fixed ones, each carrying
    // its search and its view filter, with the x deleting it
    renderSavedViews: function() {
        var holder = document.getElementById('rulesets-saved-views');
        var self = this;
        var html = '';

        rulesetsModel.savedViews().forEach(function(view) {
            html += '<button class="button-ghost rulesets-chip rulesets-saved-chip" data-saved-view="' + shared.escape(view.name) + '" ' +
                'onclick="rulesetsView.applySavedView(this, \'' + shared.escape(view.name) + '\')" ' +
                'data-tippy-content="A saved view: ' + self.describeView(view.payload) + '.">' + shared.escape(view.name) +
                '<span class="rulesets-view-x" onclick="event.stopPropagation(); rulesetsView.deleteSavedView(\'' +
                shared.escape(view.name) + '\')" data-tippy-content="Deletes this view.">' + shared.icon('x', 10) + '</span></button>';
        });

        holder.innerHTML = html;
    },

    describeView: function(payload) {
        var out = 'the ' + payload.view + ' chip' +
            (payload.query === '' ? ', no search' : ' with ' + shared.escape(payload.query) + ' in the search');
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var list = document.getElementById('problems-list');
        list.innerHTML = '<div class="problem-item problem-none">Problems found by validation and the advisory checks ' +
            'show up here on the editing screens.</div>';
    },
};

window.rulesetsView = rulesetsView;

})();
