'use strict';

(function() {

var rulesetsView = {

    config: {
        maxVisibleRows: 200,
        maxRowMatches: 3,
        maxPreviewRules: 6,
        maxPreviewEvents: 5,
        maxSavedViews: 5,
        maxRenamedRules: 6,
        maxRulesInPanel: 40,

        loadingRulesText: 'Reading the rules of',
        emptyRulesText: 'This set has no rules yet, open it to write the first one.',

        rulesetNamePattern: /^\w+(\.\w+)*$/,

        openUrls: {
            tables: '/tables/',
            editor: '/editor/',
            tests: '/tests/',
            versions: '/versions/',
            log: '/decision-log/',
            vocabulary: '/vocabulary/',
        },

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

    query: '',
    view: 'all',
    selectedId: null,
    expanded: {},

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

    whenText: function(iso) {
        return iso.slice(0, 16).replace('T', ' ');
    },

// ////////////////////////////////////////////////////////////////////////

    markHtml: function(text) {
        if (this.query.trim() === '') { return shared.escape(text); }

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
            out += '<span class="rulesets-badge rulesets-badge-live">live v' + ruleset.live_version + '</span>';
        }
        if (draft !== null) {
            out += '<span class="rulesets-badge rulesets-badge-draft">draft v' + draft + '</span>';
            out += '<button class="button-mini rulesets-publish" ' +
                'onclick="event.stopPropagation(); rulesetsView.openPublishPanel(' + ruleset.id + ', this)">publish</button>';
        }
        return out;
    },

    starHtml: function(ruleset) {
        var followed = rulesetsModel.isFollowed(ruleset.id);
        var stateClass = followed ? ' rulesets-star-on' : '';
        var hint = followed ? 'Following' : 'Follow';

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

            var ruleset = entry.ruleset;
            var selected = ruleset.id === self.selectedId ? ' rulesets-row-selected' : '';

            // Every second row is tinted, counted here rather than in CSS because
            // the rules of an expanded set sit between the rows as their own panels.
            var stripe = shown % 2 === 1 ? ' rulesets-row-stripe' : '';
            shown += 1;

            var isExpanded = self.expanded[ruleset.id] === true;
            var caret = '<span class="rulesets-caret">' +
                shared.icon(isExpanded ? 'chevron-down' : 'chevron-right', 12) + '</span>';

            html += '<div class="rulesets-row' + selected + stripe + '" data-id="' + ruleset.id + '" ' +
                'onclick="rulesetsView.select(' + ruleset.id + ')" ' +
                'ondblclick="rulesetsView.open(' + ruleset.id + ')">' +
                '<div class="rulesets-row-main">' +
                '<div class="rulesets-row-name">' + self.starHtml(ruleset) +
                '<a class="rulesets-open-link" href="' + self.config.openUrls.editor + '?ruleset=' + ruleset.id + '" ' +
                    'onclick="return rulesetsView.toggleRules(event, ' + ruleset.id + ')">' +
                    caret + self.markHtml(ruleset.name) + '</a>' +
                self.statusHtml(ruleset) + '</div>' +
                self.hitsHtml(entry.hits) +
                '</div>' +
                '</div>';

            if (isExpanded) {
                html += self.rulesPanelHtml(ruleset);
            }
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

    rulesPanelHtml: function(ruleset) {
        var self = this;
        var rules = rulesetsModel.cachedRules(ruleset.id);

        if (rules === null) {
            return '<div class="rulesets-rules">' +
                '<div class="rulesets-rules-loading"><span class="rulesets-spinner"></span>' +
                this.config.loadingRulesText + ' ' + shared.escape(ruleset.name) + '</div>' +
                '</div>';
        }

        var html = '<div class="rulesets-rules">';

        if (rules.length === 0) {
            html += '<div class="rulesets-rules-empty">' + this.config.emptyRulesText + '</div></div>';
            return html;
        }

        html += '<div class="rulesets-rules-head">' + rules.length + ' rule' + (rules.length === 1 ? '' : 's') +
            ' in ' + shared.escape(ruleset.name) + '</div>';

        rules.slice(0, this.config.maxRulesInPanel).forEach(function(rule) {
            html += '<a class="rulesets-rule" href="' + self.config.openUrls.editor + '?ruleset=' + ruleset.id +
                '&amp;rule=' + encodeURIComponent(rule.key) + '" ' +
                'onclick="event.stopPropagation()">' +
                '<span class="rulesets-rule-name">' + self.markHtml(rule.name) + '</span>' +
                '<span class="rulesets-rule-docs">' + shared.escape(rule.docs) + '</span>' +
                '<span class="rulesets-rule-shape">' + rule.conditionCount + ' condition' +
                    (rule.conditionCount === 1 ? '' : 's') + ', ' + rule.actionCount + ' action' +
                    (rule.actionCount === 1 ? '' : 's') + '</span>' +
                '</a>';
        });

        if (rules.length > this.config.maxRulesInPanel) {
            html += '<div class="rulesets-match-overflow">and ' + (rules.length - this.config.maxRulesInPanel) +
                ' more rules, the search above narrows this down.</div>';
        }

        html += '</div>';
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

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
            html += '<div class="rulesets-preview-note">Nothing new on the rulesets you follow.</div>';
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

    previewHtml: function(preview) {
        var self = this;
        var ruleset = preview.definition;
        var draft = rulesetsModel.draftVersion(ruleset);

        var html = '<div class="test-grid-title">' + shared.escape(ruleset.name) +
            '<button class="button-mini rulesets-rename" ' +
            'onclick="rulesetsView.openRenamePanel(' + ruleset.id + ', this)">rename</button></div>';

        var statusValue = (ruleset.live_version === null ? 'never published' : 'live v' + ruleset.live_version) +
            (draft === null ? '' : ', draft v' + draft + ' in progress');
        if (draft !== null) {
            statusValue += ' <button class="button-mini rulesets-publish" ' +
                'onclick="rulesetsView.openPublishPanel(' + ruleset.id + ', this)">publish</button>';
        }

        var followValue = preview.is_following ? 'yes' : 'no';

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

        html += '<div class="test-grid-title">Open in</div>' +
            '<div class="rulesets-preview-links">' +
            this.previewLinkHtml(ruleset.id, 'editor', 'Rules') +
            '<a class="rulesets-preview-link" href="' + this.config.openUrls.tables + '">Decision tables</a>' +
            this.previewLinkHtml(ruleset.id, 'tests', 'Tests and A/B') +
            this.previewLinkHtml(ruleset.id, 'versions', 'Versions') +
            this.previewLinkHtml(ruleset.id, 'log', 'Decision log') +
            this.previewLinkHtml(ruleset.id, 'vocabulary', 'Vocabulary') +
            '</div>';

        var documents = preview.document.documents;

        // A set stored before it ever got a rule carries no documents at all.
        if (documents === undefined) { documents = {}; }

        var keys = Object.keys(documents).sort(function(left, right) {
            return documents[left].name.localeCompare(documents[right].name);
        });

        if (keys.length > 0) {
            html += '<div class="test-grid-title">Rules, ' + keys.length + '</div>';

            keys.slice(0, this.config.maxPreviewRules).forEach(function(key) {
                html += '<a class="rulesets-preview-rule" href="' + self.config.openUrls.editor +
                    '?ruleset=' + ruleset.id + '&amp;rule=' + encodeURIComponent(key) + '">' +
                    shared.escape(documents[key].name) + '</a>';
            });

            if (keys.length > this.config.maxPreviewRules) {
                html += '<div class="rulesets-match-overflow">and ' + (keys.length - this.config.maxPreviewRules) +
                    ' more, the row itself lists them all</div>';
            }
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

    renderRecents: function() {
        var strip = document.getElementById('rulesets-recents');
        var html = '';

        rulesetsModel.recents.forEach(function(recent) {
            var ruleset = rulesetsModel.byId(recent.definition_id);

            if (ruleset === undefined) { return; }

            html += '<button class="button-ghost rulesets-recent-chip" ' +
                'onclick="rulesetsView.pickRecent(' + ruleset.id + ')">' +
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

    renderSavedViews: function() {
        var holder = document.getElementById('rulesets-saved-views');
        var self = this;
        var html = '';

        rulesetsModel.savedViews().forEach(function(view) {
            html += '<button class="button-ghost rulesets-chip rulesets-saved-chip" data-saved-view="' + shared.escape(view.name) + '" ' +
                'onclick="rulesetsView.applySavedView(this, \'' + shared.escape(view.name) + '\')" ' +
                'data-tippy-content="' + self.describeView(view.payload) + '">' + shared.escape(view.name) +
                '<span class="rulesets-view-x" onclick="event.stopPropagation(); rulesetsView.deleteSavedView(\'' +
                shared.escape(view.name) + '\')">' + shared.icon('x', 10) + '</span></button>';
        });

        holder.innerHTML = html;
    },

    describeView: function(payload) {
        var out = payload.view + (payload.query === '' ? '' : ', search ' + shared.escape(payload.query));
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var list = document.getElementById('problems-list');
        list.innerHTML = '<div class="problem-item problem-none">No problems.</div>';
    },
};

window.rulesetsView = rulesetsView;

})();
