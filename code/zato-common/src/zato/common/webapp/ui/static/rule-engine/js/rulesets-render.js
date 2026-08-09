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

        loadingText: 'Loading',
        emptyRulesText: 'No rules yet',
        saveViewLabel: 'Create view',
        countNoun: 'ruleset',
        countNounPlural: 'rulesets',
        clearLabel: 'Clear',
        searchDelayMilliseconds: 160,

        rulesetNamePattern: /^\w+(\.\w+)*$/,
        viewNamePattern: /^[A-Za-z0-9 ]+$/,

        facets: [
            {facet: 'status', value: 'live', field: 'live'},
            {facet: 'status', value: 'draft', field: 'draft'},
            {facet: 'followed', value: 'yes', field: 'followed'},
        ],

        groups: {
            facets: 'Filters',
            views: 'Saved views',
            text: 'Search',
        },

        // What of the browser the host application shows - the rule engine dashboard
        // turns everything on, an embedding host turns the collaboration features off
        showFollows: true,
        showFeed: true,
        showViews: true,
        showPublish: true,
        showRename: true,
        showRowMenu: true,
        showProblems: true,

        // Whether the filter input opens the suggestion pane at all - a host with
        // no facets and no saved views has nothing to suggest
        showSuggestions: true,

        // Whether the count next to the filter input is shown
        showCount: true,

        // Whether the side pane with the preview shows at all - a host where every
        // rule is always live has nothing to preview, so the list takes the width
        showSidePane: true,

        // Whether the expanded rules panel says which rules are active, and what actions
        // it offers on each rule - each action is {key, label, onRun(ruleKey, target)}
        // with an optional isShown(rule)
        showRuleState: false,
        ruleActions: [],

        // The class the action links carry - the host's own link face, so they look
        // like every other link on its screens
        ruleActionClass: 'link',

        // Which screens the host can open - only the URLs it passes render as links
        openUrls: {},

        // The screens of the preview pane's open-in strip, each rendered only when
        // its URL is among openUrls - the tables screen takes no ruleset of its own
        previewScreens: [
            {screen: 'editor', label: 'Rules', plain: false},
            {screen: 'tables', label: 'Decision tables', plain: true},
            {screen: 'tests', label: 'Tests and A/B', plain: false},
            {screen: 'versions', label: 'Versions', plain: false},
            {screen: 'log', label: 'Decision log', plain: false},
            {screen: 'vocabulary', label: 'Vocabulary', plain: false},
        ],

        // What the command bar's button says and what it runs
        newLabel: 'New ruleset',
        onNew: null,

        // A ruleset expanded and selected as soon as the screen loads, so an embedding
        // host opens straight onto the rules of the one set it cares about
        autoExpandId: null,

        // Whether the auto-expanded ruleset stays open for good - no caret, no way to
        // collapse it, its name a plain link to the editor
        lockExpanded: false,

        // Whether the expanded panel's head names the ruleset - "6 rules in alerts" -
        // or counts alone, for a host whose one ruleset needs no naming
        showRulesetInRulesHead: true,

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

    container: null,

    query: '',
    chosen: [],
    suggestions: [],
    suggestionIndex: -1,
    suggestOpen: false,
    searchTimer: null,
    selectedId: null,
    expanded: {},

// ////////////////////////////////////////////////////////////////////////

    element: function(selector) {
        var out = this.container.querySelector(selector);
        return out;
    },

    elements: function(selector) {
        var out = this.container.querySelectorAll(selector);
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        this.renderSuggestions();
        this.renderList();
        this.renderSide();
        this.renderProblems();
        shared.initTips();
    },

// ////////////////////////////////////////////////////////////////////////

    // The name a ruleset goes by on the screen, from the labels the model holds
    displayName: function(name) {
        return rulesetsModel.displayName(name);
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
        if (!this.config.showPublish) { return ''; }

        var draft = rulesetsModel.draftVersion(ruleset);
        var out = '';

        if (ruleset.live_version !== null) {
            out += '<span class="pill pill-good">live v' + ruleset.live_version + '</span>';
        }
        if (draft !== null) {
            out += '<span class="pill pill-progress">draft v' + draft + '</span>';
            out += '<button class="button-action rulesets-publish" ' +
                'data-action="open-publish" data-id="' + ruleset.id + '">Publish</button>';
        }
        return out;
    },

    starHtml: function(ruleset) {
        if (!this.config.showFollows) { return ''; }

        var followed = rulesetsModel.isFollowed(ruleset.id);
        var stateClass = followed ? ' rulesets-star-on' : '';

        var out = '<span class="rulesets-star' + stateClass + '" ' +
            'data-action="toggle-follow" data-id="' + ruleset.id + '">' +
            shared.icon('star', 13) + '</span>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    renderList: function() {
        var self = this;
        var entries = rulesetsModel.filtered(this.filters(), this.query);
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

            // A locked row stays expanded for good - no caret, nothing toggles it
            var isLocked = self.config.lockExpanded && ruleset.id === self.config.autoExpandId;
            var isExpanded = isLocked || self.expanded[ruleset.id] === true;

            // A locked row's name is a plain title, an unlocked one is the toggle link
            // with the caret sitting next to it, not inside it
            var nameHtml;

            if (isLocked) {
                nameHtml = '<span class="rulesets-row-title">' +
                    self.markHtml(self.displayName(ruleset.name)) + '</span>';
            }
            else {
                nameHtml = '<span class="rulesets-caret" ' +
                    'data-action="toggle-rules" data-id="' + ruleset.id + '">' +
                    shared.icon(isExpanded ? 'chevron-down' : 'chevron-right', 12) + '</span>' +
                    '<a class="rulesets-open-link" href="' + self.config.openUrls.editor +
                    '?ruleset=' + ruleset.id + '" ' +
                    'data-action="toggle-rules" data-id="' + ruleset.id + '">' +
                    '<span class="link">' + self.markHtml(self.displayName(ruleset.name)) + '</span></a>';
            }

            html += '<div class="rulesets-row' + selected + stripe + '" data-id="' + ruleset.id + '" ' +
                'data-action="select-ruleset">' +
                '<div class="rulesets-row-main">' +
                '<div class="rulesets-row-name">' + self.starHtml(ruleset) + nameHtml +
                self.statusHtml(ruleset) + '</div>' +
                self.hitsHtml(entry.hits) +
                '</div>' +
                '</div>';

            if (isExpanded) {
                html += self.rulesPanelHtml(ruleset);
            }
        });

        if (html === '') {
            html = '<div class="rulesets-empty">Nothing matches</div>';
        }
        if (entries.length > shown) {
            html += '<div class="rulesets-more">First ' + shown + ' of ' + entries.length + '</div>';
        }

        this.renderCount(entries.length, rulesetsModel.rulesets.length);
        this.element('#rulesets-list').innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    ruleStateHtml: function(rule) {
        if (!this.config.showRuleState) { return ''; }

        // The colours come from the host's shared status badge classes - green for
        // active, gray for not - the same pair its other screens use
        var out = rule.isActive
            ? '<span class="pill rulesets-rule-state status-badge-on">Active</span>'
            : '<span class="pill rulesets-rule-state status-badge-off">Inactive</span>';
        return out;
    },

    ruleActionsHtml: function(rule) {
        var html = '';
        var actionClass = this.config.ruleActionClass;

        this.config.ruleActions.forEach(function(action, actionIndex) {
            if (action.isShown !== undefined && !action.isShown(rule)) { return; }

            html += '<span class="' + actionClass + ' rulesets-rule-action" data-action="rule-action" ' +
                'data-index="' + actionIndex + '" data-rule="' + shared.escape(rule.key) + '">' +
                action.label + '</span>';
        });

        return html;
    },

    rulesPanelHtml: function(ruleset) {
        var self = this;
        var rules = rulesetsModel.cachedRules(ruleset.id);

        if (rules === null) {
            return '<div class="rulesets-rules">' +
                '<div class="rulesets-rules-loading"><span class="rulesets-spinner"></span>' +
                this.config.loadingText + '</div>' +
                '</div>';
        }

        var html = '<div class="rulesets-rules">';

        if (rules.length === 0) {
            html += '<div class="rulesets-rules-empty">' + this.config.emptyRulesText + '</div></div>';
            return html;
        }

        var head = rules.length + ' rule' + (rules.length === 1 ? '' : 's');
        if (this.config.showRulesetInRulesHead) {
            head += ' in ' + shared.escape(this.displayName(ruleset.name));
        }
        html += '<div class="rulesets-rules-head">' + head + '</div>';

        rules.slice(0, this.config.maxRulesInPanel).forEach(function(rule, ruleIndex) {
            html += '<a class="rulesets-rule" href="' + self.config.openUrls.editor + '?ruleset=' + ruleset.id +
                '&amp;rule=' + encodeURIComponent(rule.key) + '">' +
                '<span class="rulesets-rule-number">' + (ruleIndex + 1) + '</span>' +
                '<span class="rulesets-rule-name">' + self.markHtml(rule.name) + '</span>' +
                '<span class="rulesets-rule-docs">' + shared.escape(rule.docs) + '</span>' +
                '<span class="rulesets-rule-shape">' + rule.conditionCount + ' condition' +
                    (rule.conditionCount === 1 ? '' : 's') + '</span>' +
                '<span class="rulesets-rule-shape">' + rule.actionCount + ' action' +
                    (rule.actionCount === 1 ? '' : 's') + '</span>' +
                self.ruleStateHtml(rule) +
                self.ruleActionsHtml(rule) +
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

        // A host without the pane has no preview to paint - nothing to do here
        if (!this.config.showSidePane) { return; }

        var pane = this.element('#rulesets-side');

        if (this.selectedId === null) {
            pane.innerHTML = this.config.showFeed ? this.feedHtml() : '';
            shared.initTips();
            return;
        }

        rulesetsModel.preview(this.selectedId, function(preview) {
            pane.innerHTML = self.previewHtml(preview);
            shared.initTips();
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
            var name = ruleset === undefined ? 'ruleset ' + entry.definition_id : self.displayName(ruleset.name);

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

        var html = '<div class="test-grid-title">' + shared.escape(this.displayName(ruleset.name));
        if (this.config.showRename) {
            html += '<button class="button-mini rulesets-rename" ' +
                'data-action="open-rename" data-id="' + ruleset.id + '">rename</button>';
        }
        html += '</div>';

        var statusValue = ruleset.live_version === null ? 'never published' : 'live v' + ruleset.live_version;
        if (this.config.showPublish) {
            statusValue += draft === null ? '' : ', draft v' + draft + ' in progress';
            if (draft !== null) {
                statusValue += ' <button class="button-action rulesets-publish" ' +
                    'data-action="open-publish" data-id="' + ruleset.id + '">Publish</button>';
            }
        }

        html += '<table class="test-grid"><tbody>';
        html += '<tr><td class="test-label-cell">status</td><td class="test-value-cell log-value-readonly">' +
            statusValue + '</td></tr>';
        html += '<tr><td class="test-label-cell">created</td><td class="test-value-cell log-value-readonly">' +
            this.whenText(ruleset.created_at) + '</td></tr>';
        html += '<tr><td class="test-label-cell">last change</td><td class="test-value-cell log-value-readonly">' +
            this.whenText(ruleset.updated_at) + '</td></tr>';
        if (this.config.showFollows) {
            html += '<tr><td class="test-label-cell">followed</td><td class="test-value-cell log-value-readonly">' +
                (preview.is_following ? 'yes' : 'no') + '</td></tr>';
        }
        html += '</tbody></table>';

        html += this.previewLinksHtml(ruleset.id);

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
                    ' more</div>';
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

    // The open-in strip shows only the screens the host has - one link for web-admin,
    // the whole dashboard for the rule engine's own pages
    previewLinksHtml: function(id) {
        var self = this;
        var links = '';

        this.config.previewScreens.forEach(function(entry) {
            if (self.config.openUrls[entry.screen] === undefined) { return; }

            var href = self.config.openUrls[entry.screen] + (entry.plain ? '' : '?ruleset=' + id);
            links += '<a class="rulesets-preview-link" href="' + href + '">' + entry.label + '</a>';
        });

        if (links === '') { return ''; }

        var out = '<div class="test-grid-title">Open in</div>' +
            '<div class="rulesets-preview-links">' + links + '</div>';
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    renderCount: function(matching, total) {
        var count = this.element('#rulesets-count');
        var clear = this.element('#rulesets-clear');
        var narrowed = this.narrowed();
        var reading = narrowed ? matching + ' of ' + total : String(total);
        var noun = total === 1 ? this.config.countNoun : this.config.countNounPlural;

        // A host without the count still keeps the clear button, so a typed query can be undone
        count.textContent = this.config.showCount ? reading + ' ' + noun : '';
        clear.style.visibility = narrowed ? 'visible' : 'hidden';
    },

    renderSuggestions: function() {
        var pane = this.element('#rulesets-suggest');
        var groups = this.config.groups;
        var self = this;
        var html = '<div class="command-suggest-drag">' + shared.icon('grip-horizontal', 12) + '</div>';

        [groups.facets, groups.views, groups.text].forEach(function(group) {
            var rows = '';

            self.suggestions.forEach(function(entry, index) {
                if (entry.group !== group) { return; }
                rows += self.suggestRowHtml(entry, index);
            });

            // The saved views group holds the button that makes one, so its title
            // is always there when the host has saved views at all
            if (rows === '' && (group !== groups.views || !self.config.showViews)) { return; }

            html += self.suggestTitleHtml(group) + rows;
        });

        pane.innerHTML = html;
        pane.classList.toggle('command-suggest-open', this.suggestOpen);
    },

    suggestTitleHtml: function(group) {
        var button = '';

        if (group === this.config.groups.views && this.config.showViews) {
            button = '<button class="button-mini command-suggest-new" id="rulesets-save-view" ' +
                'data-mouse-action="open-save-view">' + this.config.saveViewLabel + '</button>';
        }

        return '<div class="command-suggest-title">' + group + button + '</div>';
    },

    suggestRowHtml: function(entry, index) {
        var html = '';
        var active = index === this.suggestionIndex ? ' command-suggest-row-active' : '';
        var check = entry.token !== null && this.isChosen(entry.token) ? shared.icon('check', 12) : '';
        var tail = '<span class="command-suggest-count">' +
            (entry.count === null ? '' : entry.count) + '</span>';

        // A saved view carries its own way out, so a view is dropped where it is offered
        if (entry.view !== null) {
            tail = '<button class="command-suggest-drop" ' +
                'data-mouse-action="drop-view" data-index="' + index + '">' + shared.icon('x', 10) + '</button>';
        }

        html += '<div class="command-suggest-row' + active + '" ' +
            'data-mouse-action="pick" data-index="' + index + '">' +
            '<span class="command-suggest-check">' + check + '</span>' +
            '<span class="command-suggest-facet">' + entry.facet + '</span>' +
            '<span class="command-suggest-value">' + shared.escape(entry.value) + '</span>' +
            tail + '</div>';

        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        if (!this.config.showProblems) { return; }

        var list = this.element('#problems-list');
        list.innerHTML = '<div class="problem-item problem-none">No problems.</div>';
    },
};

window.rulesetsView = rulesetsView;

})();
