'use strict';

// Rendering for the versions and changes screen: the linear timeline,
// the grouped structural diff with word-level changes inside every
// updated rule, viewed-progress tracking, the outcome comparison, the
// anchored review comments and the approval card. Event handlers live
// in versions-actions.js, which augments this namespace.

(function() {

var versionsView = {

    config: {
        // The outcome section lists at most this many changed scenarios,
        // the tests and simulation screen shows the rest
        maxOutcomeRows: 5,

        // Every history event type as the phrase the activity feed shows
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
    changesOnly: false,
    splitView: true,

    stateBadges: {
        added: '<span class="versions-badge versions-badge-added">added</span>',
        deleted: '<span class="versions-badge versions-badge-deleted">deleted</span>',
        renamed: '<span class="versions-badge versions-badge-renamed">renamed</span>',
        updated: '<span class="versions-badge versions-badge-updated">updated</span>',
        unchanged: '',
    },

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        this.renderSubtitle();
        this.renderTimeline();
        this.renderSelects();
        this.renderDetail();
        this.renderReview();
        this.renderActivity();
        this.renderProblems();
        shared.initTips();
    },

    renderSubtitle: function() {
        var text = versionsModel.rulesetName === ''
            ? 'no ruleset stored yet'
            : versionsModel.rulesetName + ' \u00b7 every version keeps its comment \u00b7 restoring never renumbers anything';
        document.getElementById('main-subtitle').textContent = text;
    },

// ////////////////////////////////////////////////////////////////////////

    // Timestamps come from the views as ISO strings, the screen shows
    // the readable date-and-minute part
    whenText: function(iso) {
        return iso.slice(0, 16).replace('T', ' ');
    },

// ////////////////////////////////////////////////////////////////////////

    renderTimeline: function() {
        var self = this;
        var html = '';

        versionsModel.versions.forEach(function(version) {
            var classes = 'versions-timeline-item';
            if (version.number === versionsModel.fromNumber || version.number === versionsModel.toNumber) {
                classes += ' versions-timeline-item-comparing';
            }

            var badges = '';
            if (version.number === versionsModel.liveVersion) {
                badges += '<span class="versions-badge versions-badge-live" data-tippy-content="A snapshot ' +
                    'was taken when this version went live, so this exact state can go live again as-is.">live</span>';
            } else if (versionsModel.liveVersion === null || version.number > versionsModel.liveVersion) {
                // Nothing published yet makes every version a draft
                badges += '<span class="versions-badge versions-badge-draft">draft</span>';
            }
            if (version.restoredFrom !== null) {
                badges += '<span class="versions-badge versions-badge-restored">from v' + version.restoredFrom + '</span>';
            }

            var restore = version.number === versionsModel.currentVersion ? '' :
                '<button class="button-mini versions-restore" ' +
                'onclick="versionsView.restore(event, ' + version.number + ', this)" ' +
                'data-tippy-content="Creates a new version from this exact state and publishes it. ' +
                'The timeline only ever grows, nothing is renumbered or hidden.">Restore</button>';

            html += '<div class="' + classes + '" onclick="versionsView.pickVersion(' + version.number + ')">' +
                '<div class="versions-timeline-top">' +
                '<span class="versions-timeline-number">v' + version.number + '</span>' +
                '<span class="versions-timeline-author">' + shared.escape(version.author) + ', ' +
                self.whenText(version.createdAt) + '</span>' + badges + restore + '</div>' +
                '<div class="versions-timeline-comment">' + shared.escape(version.comment) + '</div>' +
                '</div>';
        });

        document.getElementById('versions-timeline').innerHTML = html;
    },

    renderSelects: function() {
        var fromSelect = document.getElementById('versions-from');
        var toSelect = document.getElementById('versions-to');

        var options = versionsModel.versions.map(function(version) {
            var suffix = '';
            if (version.number === versionsModel.liveVersion) {
                suffix = ' (live)';
            } else if (versionsModel.liveVersion === null || version.number > versionsModel.liveVersion) {
                suffix = ' (draft)';
            }
            return '<option value="' + version.number + '">v' + version.number + suffix + '</option>';
        }).join('');

        fromSelect.innerHTML = options;
        toSelect.innerHTML = options;
        fromSelect.value = String(versionsModel.fromNumber);
        toSelect.value = String(versionsModel.toNumber);
    },

// ////////////////////////////////////////////////////////////////////////

    wordDiffHtml: function(segments, only) {
        var out = segments.map(function(segment) {
            if (segment.text === '\n') { return '<br>'; }
            if (segment.type === 'same') { return shared.escape(segment.text); }
            if (only !== undefined && segment.type !== only) { return ''; }
            var className = segment.type === 'del' ? 'versions-word-deleted' : 'versions-word-inserted';
            return '<span class="' + className + '">' + shared.escape(segment.text) + '</span>';
        }).filter(function(part) { return part !== ''; }).join(' ');
        return out;
    },

    renderedHtml: function(text) {
        var out = text.split('\n').map(function(line) { return shared.escape(line); }).join('<br>');
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    // The head every rule card shares: name, badge, the viewed toggle
    // and the count of comments anchored to this rule - a renamed rule
    // shows both names while its key follows the new one
    ruleHeadHtml: function(name, state, displayName) {
        var key = 'rule-' + name;
        var viewed = versionsModel.viewed[key] === true;

        var viewedControl = '<label class="versions-viewed-toggle" data-tippy-content="Marking a change as viewed ' +
            'dims it and counts it into the progress bar, the way large reviews stay tractable.">' +
            '<input type="checkbox"' + (viewed ? ' checked' : '') +
            ' onchange="versionsView.toggleViewed(\'' + shared.escape(key) + '\', this.checked)"> viewed</label>';

        var commentCount = versionsModel.commentsFor(key).length;
        var commentMark = commentCount > 0 ? '<span class="versions-comment-mark" data-tippy-content="' +
            commentCount + ' comment(s) anchored to this rule, shown under the diff.">' + commentCount + '</span>' : '';

        var out = '<div class="versions-rule-head">' + shared.escape(displayName) + commentMark +
            this.stateBadges[state] + viewedControl + '</div>';
        return out;
    },

    // One updated rule: both rendered forms word-diffed, side by side
    // or as one merged text, and the changed blocks named
    updatedRuleHtml: function(entry) {
        var key = 'rule-' + entry.rule;
        var viewed = versionsModel.viewed[key] === true;
        var html = '<div class="versions-rule' + (viewed ? ' versions-viewed' : '') + '">';

        html += this.ruleHeadHtml(entry.rule, 'updated', entry.rule);
        html += '<div class="versions-rule-blocks">changed: ' + entry.changed.join(', ') + '</div>';

        var segments = versionsModel.wordDiff(entry.old_rendered, entry.new_rendered);
        if (this.splitView) {
            html += '<div class="versions-rule-split">' +
                '<div class="versions-rule-side"><span class="versions-side-tag">v' + versionsModel.fromNumber +
                '</span> ' + this.wordDiffHtml(segments, 'del') + '</div>' +
                '<div class="versions-rule-side"><span class="versions-side-tag">v' + versionsModel.toNumber +
                '</span> ' + this.wordDiffHtml(segments, 'ins') + '</div></div>';
        } else {
            html += '<div class="versions-rule-text">' + this.wordDiffHtml(segments) + '</div>';
        }

        html += '</div>';
        return html;
    },

    // One added, deleted or renamed rule: its one rendered form, tinted
    plainRuleHtml: function(name, state, rendered, displayName) {
        var key = 'rule-' + name;
        var viewed = versionsModel.viewed[key] === true;

        var out = '<div class="versions-rule' + (viewed ? ' versions-viewed' : '') + '">' +
            this.ruleHeadHtml(name, state, displayName) +
            '<div class="versions-rule-text versions-rule-' + state + '">' + this.renderedHtml(rendered) + '</div>' +
            '</div>';
        return out;
    },

    rulesDiffHtml: function() {
        var self = this;
        var comparison = versionsModel.comparison;
        var html = '';

        comparison.updated.forEach(function(entry) { html += self.updatedRuleHtml(entry); });

        comparison.renamed.forEach(function(entry) {
            var head = entry.old_rule + ' is now ' + entry.new_rule;
            html += self.plainRuleHtml(entry.new_rule, 'renamed', entry.rendered, head);
        });

        comparison.added.forEach(function(entry) {
            html += self.plainRuleHtml(entry.rule, 'added', entry.rendered, entry.rule);
        });
        comparison.deleted.forEach(function(entry) {
            html += self.plainRuleHtml(entry.rule, 'deleted', entry.rendered, entry.rule);
        });

        if (!this.changesOnly) {
            comparison.unchanged.forEach(function(entry) {
                html += '<div class="versions-rule versions-rule-unchanged-row">' +
                    shared.escape(entry.rule) + '<span class="versions-unchanged-note">unchanged</span></div>';
            });
        }

        if (html === '') {
            html = '<div class="versions-note">The two versions agree on every rule.</div>';
        }

        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    // The outcome comparison: both versions replayed the stored test
    // set's scenarios, so the reviewer sees which decisions would change,
    // not only what text changed
    outcomeDiffHtml: function() {
        var self = this;
        var outcome = versionsModel.outcome;

        if (outcome === null) {
            return '<div class="versions-note">The outcome comparison replays a stored test set against both versions. ' +
                'It runs when the compared versions differ and a test set exists.</div>';
        }

        var html = '<div class="versions-note">Both versions ran against ' + shared.escape(versionsModel.suiteName) +
            ', ' + outcome.total + ' scenario(s): <b>' + outcome.changed + ' would change</b>, ' +
            outcome.unchanged + ' would not, ' + outcome.errors + ' errored.</div>';

        var changed = outcome.scenarios.filter(function(entry) { return entry.status === 'changed'; });
        if (changed.length === 0) { return html; }

        html += '<table class="versions-outcome-grid"><tr><th>Scenario</th><th>What changes</th><th>Changed by</th></tr>';
        changed.slice(0, this.config.maxOutcomeRows).forEach(function(entry) {
            var parts = entry.changes.map(function(change) {
                var before = change.old === null ? 'no decision' : change.old;
                var after = change.new === null ? 'no decision' : change.new;
                return change.field + ': ' + before + ' becomes ' + after;
            });
            var why = entry.fired_only_new.concat(entry.fired_only_old).join(', ');
            html += '<tr><td>' + shared.escape(entry.scenario) + '</td>' +
                '<td>' + shared.escape(parts.join(', ')) + '</td>' +
                '<td>' + shared.escape(why) + '</td></tr>';
        });
        html += '</table>';

        if (changed.length > self.config.maxOutcomeRows) {
            html += '<div class="versions-note">' + (changed.length - self.config.maxOutcomeRows) +
                ' more on the tests and simulation screen.</div>';
        }

        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    progressHtml: function() {
        var keys = versionsModel.reviewableKeys();
        var viewedCount = keys.filter(function(key) { return versionsModel.viewed[key] === true; }).length;
        var share = keys.length === 0 ? 1 : viewedCount / keys.length;

        var out = '<div class="versions-progress"><span class="versions-progress-text">' +
            viewedCount + ' of ' + keys.length + ' changes viewed</span>' +
            '<span class="versions-progress-bar"><span class="versions-progress-fill" style="width:' +
            Math.round(share * 100) + '%"></span></span></div>';
        return out;
    },

    renderDetail: function() {
        var pane = document.getElementById('versions-detail-pane');

        if (versionsModel.comparison === null) {
            pane.innerHTML = '<div class="versions-note">No ruleset stored yet. Author one in the editor first.</div>';
            return;
        }

        var counts = versionsModel.counts();
        var html = '';

        html += '<div class="versions-summary">Comparing v' + versionsModel.fromNumber +
            ' with v' + versionsModel.toNumber + ', matched by rule, never by line: ' +
            '<span class="versions-count-added">' + counts.added + ' added</span>, ' +
            '<span class="versions-count-deleted">' + counts.deleted + ' deleted</span>, ' +
            '<span class="versions-count-renamed">' + counts.renamed + ' renamed</span>, ' +
            '<span class="versions-count-updated">' + counts.updated + ' updated</span>, ' +
            counts.unchanged + ' unchanged. A renamed rule is a rename, never a delete plus an add.</div>';

        html += this.progressHtml();

        html += '<div class="versions-section-title">Rules</div>';
        html += this.rulesDiffHtml();

        html += '<div class="versions-section-title">Decisions that would change</div>';
        html += this.outcomeDiffHtml();

        html += '<div class="versions-section-title">Comments, anchored to the rules they are about</div>';
        html += this.commentsHtml();

        pane.innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    eventLine: function(entry) {
        var out = this.config.eventPhrases[entry.event_type];
        if (entry.version !== null) { out += ' (v' + entry.version + ')'; }
        return out;
    },

    renderActivity: function() {
        var self = this;
        var html = versionsModel.events.map(function(entry) {
            return '<div class="versions-activity-item"><span class="versions-activity-who">' +
                shared.escape(entry.actor) + ', ' + self.whenText(entry.created_at) + '</span>' +
                '<div>' + self.eventLine(entry) + '</div></div>';
        }).join('');
        document.getElementById('versions-activity').innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var items = [];

        if (versionsModel.comparison !== null) {
            var keys = versionsModel.reviewableKeys();
            var unviewed = keys.filter(function(key) { return versionsModel.viewed[key] !== true; }).length;

            if (unviewed > 0) {
                items.push('<div class="problem-item"><span class="status-dot status-dot-warning"></span>' +
                    '<span>' + unviewed + ' change(s) not yet marked as viewed.</span></div>');
            }

            var commentCount = versionsModel.comments().length;
            if (commentCount > 0) {
                items.push('<div class="problem-item"><span class="status-dot status-dot-warning"></span>' +
                    '<span>' + commentCount + ' comment(s) anchored to this version\'s rules.</span></div>');
            }
        }

        var approval = versionsModel.approval;
        if (approval !== null && approval.gate_enabled) {
            if (!approval.is_approved) {
                items.push('<div class="problem-item"><span class="status-dot status-dot-error"></span>' +
                    '<span>The approval gate is on and v' + approval.version +
                    ' has no approval yet, so it cannot go live.</span></div>');
            } else if (!approval.content_matches) {
                items.push('<div class="problem-item"><span class="status-dot status-dot-error"></span>' +
                    '<span>The stored content of v' + approval.version +
                    ' differs from what was approved, so it cannot go live.</span></div>');
            }
        }

        if (versionsModel.outcome !== null && versionsModel.outcome.changed > 0) {
            items.push('<div class="problem-item"><span class="status-dot status-dot-information"></span>' +
                '<span>' + versionsModel.outcome.changed + ' scenario(s) of ' +
                shared.escape(versionsModel.suiteName) + ' would decide differently. Advisory, not blocking.</span></div>');
        }

        document.getElementById('problems-head').textContent = 'Before this can go live (' + items.length + ')';
        document.getElementById('problems-list').innerHTML = items.join('');
    },
};

window.versionsView = versionsView;

})();
