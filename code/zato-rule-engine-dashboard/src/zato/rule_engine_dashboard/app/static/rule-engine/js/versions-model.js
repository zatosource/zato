'use strict';

(function() {

var versionsModel = {

    config: {
        restoreComment: function(number) { return 'Restored as-is from version ' + number + '.'; },

        urls: {
            rulesets: '/rules/rulesets/?object_type=ruleset',
            suites: '/rules/test-sets/',
            timeline: function(id) { return '/rules/rulesets/' + id + '/timeline/'; },
            diff: function(id, oldNumber, newNumber) {
                return '/rules/rulesets/' + id + '/diff/?old=' + oldNumber + '&new=' + newNumber;
            },
            rollback: function(id) { return '/rules/rulesets/' + id + '/rollback/'; },
            compareOutcomes: function(id) { return '/rules/rulesets/' + id + '/compare-outcomes/'; },
            comment: function(id) { return '/rules/rulesets/' + id + '/comment/'; },
            publish: function(id) { return '/rules/rulesets/' + id + '/publish/'; },
            approvalStatus: function(id, version) { return '/rules/rulesets/' + id + '/approvals/' + version + '/'; },
            approve: function(id, version) { return '/rules/rulesets/' + id + '/approvals/' + version + '/approve/'; },
            setGate: function(id) { return '/rules/rulesets/' + id + '/approvals/gate/'; },
            setSelfApproval: function(id) { return '/rules/rulesets/' + id + '/approvals/self-approval/'; },
            preview: function(id) { return '/rules/rulesets/' + id + '/preview/'; },
        },
    },

    rulesetId: null,
    rulesetName: '',
    currentVersion: null,
    liveVersion: null,

    events: [],
    versions: [],

    fromNumber: null,
    toNumber: null,
    comparison: null,
    approval: null,

    suiteName: '',
    scenarios: [],
    outcome: null,

    viewed: {},

// ////////////////////////////////////////////////////////////////////////

    load: function(onDone) {
        var self = this;
        var wanted = new URLSearchParams(window.location.search).get('ruleset');

        data.get(this.config.urls.rulesets, function(payload) {
            var records = payload.items;
            if (wanted !== null) {
                records = records.filter(function(item) { return item.id === parseInt(wanted); });
            }

            if (records.length === 0) {
                onDone();
                return;
            }

            var record = records[0];
            self.rulesetId = record.id;
            self.rulesetName = record.name;

            self.loadTimeline(function() {
                self.loadScenarios(onDone);
            });
        }, data.reportError);
    },

    loadTimeline: function(onDone) {
        var self = this;

        data.get(this.config.urls.timeline(this.rulesetId), function(payload) {
            self.currentVersion = payload.definition.current_version;
            self.liveVersion = payload.definition.live_version;
            self.events = payload.events;
            self.versions = self.versionsFromEvents();

            if (self.toNumber === null) {
                self.toNumber = self.currentVersion;
                var noLiveBaseline = self.liveVersion === null || self.liveVersion === self.currentVersion;
                if (noLiveBaseline) {
                    self.fromNumber = self.currentVersion > 1 ? self.currentVersion - 1 : self.currentVersion;
                } else {
                    self.fromNumber = self.liveVersion;
                }
            }

            onDone();
        }, data.reportError);
    },

    loadScenarios: function(onDone) {
        var self = this;

        data.get(this.config.urls.suites, function(payload) {
            if (payload.items.length === 0) {
                onDone();
                return;
            }

            data.get(self.config.urls.preview(payload.items[0].id), function(preview) {
                self.suiteName = preview.document.name;
                self.scenarios = preview.document.scenarios;
                onDone();
            }, data.reportError);
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    versionsFromEvents: function() {
        var out = [];

        this.events.forEach(function(entry) {
            var isCreated = entry.event_type === 'version.created';
            var isRestored = entry.event_type === 'version.restored';
            if (!isCreated && !isRestored) { return; }

            out.push({
                number: entry.version,
                author: entry.actor,
                createdAt: entry.created_at,
                comment: entry.payload.comment,
                restoredFrom: isRestored ? entry.payload.source_version : null,
            });
        });

        return out;
    },

    compare: function(onDone) {
        var self = this;
        this.viewed = {};
        this.outcome = null;

        var url = this.config.urls.diff(this.rulesetId, this.fromNumber, this.toNumber);
        data.get(url, function(payload) {
            self.comparison = payload;
            self.loadApproval(function() {
                self.loadOutcome(onDone);
            });
        }, data.reportError);
    },

    loadApproval: function(onDone) {
        var self = this;

        data.get(this.config.urls.approvalStatus(this.rulesetId, this.toNumber), function(payload) {
            self.approval = payload;
            onDone();
        }, data.reportError);
    },

    loadOutcome: function(onDone) {
        var self = this;

        var comparable = this.scenarios.length > 0 && this.fromNumber !== this.toNumber;
        if (!comparable) {
            onDone();
            return;
        }

        var body = {old_version: this.fromNumber, new_version: this.toNumber, scenarios: this.scenarios};
        data.post(this.config.urls.compareOutcomes(this.rulesetId), body, function(payload) {
            self.outcome = payload;
            onDone();
        }, data.reportError);
    },

// ////////////////////////////////////////////////////////////////////////

    counts: function() {
        var out = {
            added: this.comparison.added.length,
            deleted: this.comparison.deleted.length,
            renamed: this.comparison.renamed.length,
            updated: this.comparison.updated.length,
            unchanged: this.comparison.unchanged.length,
        };
        return out;
    },

    reviewableKeys: function() {
        var out = [];

        this.comparison.updated.forEach(function(entry) { out.push('rule-' + entry.rule); });
        this.comparison.renamed.forEach(function(entry) { out.push('rule-' + entry.new_rule); });
        this.comparison.added.forEach(function(entry) { out.push('rule-' + entry.rule); });
        this.comparison.deleted.forEach(function(entry) { out.push('rule-' + entry.rule); });

        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    comments: function() {
        var self = this;
        var out = [];

        this.events.forEach(function(entry) {
            var isComment = entry.event_type === 'review.commented';
            if (isComment && entry.version === self.toNumber) {
                out.unshift({
                    anchor: entry.payload.anchor,
                    text: entry.payload.text,
                    author: entry.actor,
                    createdAt: entry.created_at,
                });
            }
        });

        return out;
    },

    commentsFor: function(anchor) {
        var out = this.comments().filter(function(comment) { return comment.anchor === anchor; });
        return out;
    },

// ////////////////////////////////////////////////////////////////////////

    commonSubsequence: function(first, second) {
        var lengths = [];
        for (var i = 0; i <= first.length; i++) { lengths.push(new Array(second.length + 1).fill(0)); }

        for (var firstIndex = 1; firstIndex <= first.length; firstIndex++) {
            for (var secondIndex = 1; secondIndex <= second.length; secondIndex++) {
                if (first[firstIndex - 1] === second[secondIndex - 1]) {
                    lengths[firstIndex][secondIndex] = lengths[firstIndex - 1][secondIndex - 1] + 1;
                } else {
                    lengths[firstIndex][secondIndex] =
                        Math.max(lengths[firstIndex - 1][secondIndex], lengths[firstIndex][secondIndex - 1]);
                }
            }
        }

        var out = [];
        var walkFirst = first.length;
        var walkSecond = second.length;
        while (walkFirst > 0 && walkSecond > 0) {
            if (first[walkFirst - 1] === second[walkSecond - 1]) {
                out.unshift(first[walkFirst - 1]);
                walkFirst--; walkSecond--;
            } else if (lengths[walkFirst - 1][walkSecond] >= lengths[walkFirst][walkSecond - 1]) {
                walkFirst--;
            } else {
                walkSecond--;
            }
        }

        return out;
    },

    wordDiff: function(oldText, newText) {
        var oldWords = oldText.split(/(\n)| /).filter(function(token) { return token !== undefined && token !== ''; });
        var newWords = newText.split(/(\n)| /).filter(function(token) { return token !== undefined && token !== ''; });
        var stable = this.commonSubsequence(oldWords, newWords);

        var out = [];
        var oldIndex = 0;
        var newIndex = 0;

        stable.forEach(function(word) {
            while (oldWords[oldIndex] !== word) { out.push({type: 'del', text: oldWords[oldIndex]}); oldIndex++; }
            while (newWords[newIndex] !== word) { out.push({type: 'ins', text: newWords[newIndex]}); newIndex++; }
            out.push({type: 'same', text: word});
            oldIndex++; newIndex++;
        });
        while (oldIndex < oldWords.length) { out.push({type: 'del', text: oldWords[oldIndex]}); oldIndex++; }
        while (newIndex < newWords.length) { out.push({type: 'ins', text: newWords[newIndex]}); newIndex++; }

        return out;
    },
};

window.versionsModel = versionsModel;

})();
