'use strict';

(function() {

var rulesetsView = {

    config: {
        maxVisibleRows: 200,
        maxRulesInPanel: 40,

        loadingText: 'Loading',
        emptyRulesText: 'No rules yet',
        noMatchesText: 'Nothing matches',
        clearLabel: 'Clear',
        searchDelayMilliseconds: 160,

        // The address bar parameter the typed query is kept under, so a filtered
        // listing can be bookmarked - null keeps the address bar untouched
        queryURLKey: null,

        // The actions the expanded rules panel offers on each rule - each action is
        // {label, onRun(ruleKey, target)} with an optional isShown(rule)
        ruleActions: [],

        // The class the action links carry - the host's own link face, so they look
        // like every other link on its screens
        ruleActionClass: 'link',

        // The screens the host can open, keyed by their name
        openUrls: {},

        // What the command bar's button says and what it runs
        newLabel: 'New ruleset',
        onNew: null,

        // A ruleset expanded and selected as soon as the screen loads, which stays open for good -
        // no caret, no way to collapse it, its name a plain title
        autoExpandId: null,
    },

    container: null,

    query: '',
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
        this.renderList();
        shared.initTips();
    },

// ////////////////////////////////////////////////////////////////////////

    // The name a ruleset goes by on the screen, from the labels the model holds
    displayName: function(name) {
        return rulesetsModel.displayName(name);
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

    renderList: function() {
        var self = this;
        var entries = rulesetsModel.filtered(this.query);
        var cap = this.config.maxVisibleRows;
        var html = '';
        var shown = 0;

        entries.forEach(function(entry) {
            if (shown >= cap) { return; }

            var ruleset = entry.ruleset;
            var selected = ruleset.id === self.selectedId ? ' rulesets-row-selected' : '';
            var nameText = shared.escape(self.displayName(ruleset.name));

            // Every second row is tinted, counted here rather than in CSS because
            // the rules of an expanded set sit between the rows as their own panels.
            var stripe = shown % 2 === 1 ? ' rulesets-row-stripe' : '';
            shown += 1;

            // A locked row stays expanded for good - no caret, nothing toggles it
            var isLocked = ruleset.id === self.config.autoExpandId;
            var isExpanded = isLocked || self.expanded[ruleset.id] === true;

            // A locked row's name is a plain title, an unlocked one is the toggle link
            // with the caret sitting next to it, not inside it
            var nameHtml;

            if (isLocked) {
                nameHtml = '<span class="rulesets-row-title">' + nameText + '</span>';
            }
            else {
                nameHtml = '<span class="rulesets-caret" ' +
                    'data-action="toggle-rules" data-id="' + ruleset.id + '">' +
                    shared.icon(isExpanded ? 'chevron-down' : 'chevron-right', 12) + '</span>' +
                    '<a class="rulesets-open-link" href="' + self.config.openUrls.editor +
                    '?ruleset=' + ruleset.id + '" ' +
                    'data-action="toggle-rules" data-id="' + ruleset.id + '">' +
                    '<span class="link">' + nameText + '</span></a>';
            }

            html += '<div class="rulesets-row' + selected + stripe + '" data-id="' + ruleset.id + '" ' +
                'data-action="select-ruleset">' +
                '<div class="rulesets-row-main">' +
                '<div class="rulesets-row-name">' + nameHtml + '</div>' +
                '</div>' +
                '</div>';

            if (isExpanded) {
                html += self.rulesPanelHtml(ruleset);
            }
        });

        if (html === '') {
            html = '<div class="rulesets-empty">' + this.config.noMatchesText + '</div>';
        }
        if (entries.length > shown) {
            html += '<div class="rulesets-more">First ' + shown + ' of ' + entries.length + '</div>';
        }

        this.renderClear();
        this.element('#rulesets-list').innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    // The rule's active state is worn by the row itself - a green wash on the name,
    // the ordinal and its node on the spine in the deeper green - not said in a pill
    ruleStateClass: function(rule) {
        return rule.isActive ? ' rulesets-rule-on' : ' rulesets-rule-off';
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

        if (html === '') { return ''; }

        // The links sit in a strip of their own, layered above the name's stretched
        // link, so a click landing between them reaches neither link and opens nothing
        return '<span class="rulesets-rule-actions">' + html + '</span>';
    },

    // The rules of one set narrowed to the query - a rule stays when the query is in its
    // name or docs, or when the server found the query inside the rule's own text
    matchingRules: function(ruleset, rules, needle) {
        var hitKeys = {};
        rulesetsModel.hitsFor(ruleset.id).forEach(function(hit) { hitKeys[hit.rule] = true; });

        var out = rules.filter(function(rule) {
            if (rule.name.toLowerCase().indexOf(needle) > -1) { return true; }
            if (rule.docs.toLowerCase().indexOf(needle) > -1) { return true; }
            return hitKeys[rule.key] === true;
        });
        return out;
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

        // Each rule keeps the ordinal it has in the full set, so the numbers
        // do not shift while a filter narrows the panel down
        var ordinals = {};
        rules.forEach(function(rule, ruleIndex) { ordinals[rule.key] = ruleIndex + 1; });

        // A typed query narrows the panel to the rules it touches
        var needle = this.query.trim().toLowerCase();
        var isNarrowed = needle !== '';

        if (isNarrowed) {
            rules = this.matchingRules(ruleset, rules, needle);
        }

        var html = '<div class="rulesets-rules">';

        if (rules.length === 0) {
            var emptyText = isNarrowed ? this.config.noMatchesText : this.config.emptyRulesText;
            html += '<div class="rulesets-rules-empty">' + emptyText + '</div></div>';
            return html;
        }

        rules.slice(0, this.config.maxRulesInPanel).forEach(function(rule) {
            var href = self.config.openUrls.editor + '?ruleset=' + ruleset.id +
                '&amp;rule=' + encodeURIComponent(rule.key);

            // The name is the row's one real link - its stretched overlay makes the
            // whole row lead to the editor without wrapping everything in an anchor
            html += '<div class="rulesets-rule' + self.ruleStateClass(rule) + '">' +
                '<span class="rulesets-rule-number">' + ordinals[rule.key] + '</span>' +
                '<a class="rulesets-rule-name" href="' + href + '">' + self.markHtml(rule.name) + '</a>' +
                '<span class="rulesets-rule-docs">' + self.markHtml(rule.docs) + '</span>' +
                self.ruleActionsHtml(rule) +
                '</div>';
        });

        if (rules.length > this.config.maxRulesInPanel) {
            html += '<div class="rulesets-match-overflow">and ' + (rules.length - this.config.maxRulesInPanel) +
                ' more rules, the search above narrows this down.</div>';
        }

        html += '</div>';
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    // The clear button shows only while a typed query narrows the list
    renderClear: function() {
        var clear = this.element('#rulesets-clear');
        var narrowed = this.query.trim() !== '';

        clear.style.visibility = narrowed ? 'visible' : 'hidden';
    },
};

window.rulesetsView = rulesetsView;

})();
