'use strict';

(function() {

var notifyView = {

    addKind: null,

    isLoadingTargets: false,

// ////////////////////////////////////////////////////////////////////////

    render: function() {
        this.renderSubtitle();
        this.renderRulesetSelect();
        this.renderDestinations();
        this.renderCredentials();
        this.renderProblems();
        shared.initTips();
    },

    renderSubtitle: function() {
        var text = notifyModel.rulesetName === ''
            ? 'no ruleset stored yet'
            : notifyModel.rulesetName + ' \u00b7 who hears about this ruleset\u2019s life, and through which channel';
        document.getElementById('main-subtitle').textContent = text;
    },

    renderRulesetSelect: function() {
        var select = document.getElementById('notify-ruleset');
        var html = '';

        notifyModel.rulesets.forEach(function(record) {
            var selected = record.id === notifyModel.rulesetId ? ' selected' : '';
            html += '<option value="' + record.id + '"' + selected + '>' + shared.escape(record.name) + '</option>';
        });

        select.innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    whenText: function(iso) {
        return iso.slice(0, 16).replace('T', ' ');
    },

    statusHtml: function(record) {
        if (record.last_status === null) {
            return '<span class="status-dot status-dot-information"></span>nothing delivered yet';
        }

        if (record.last_status === 'error') {
            return '<span class="status-dot status-dot-error"></span>' +
                '<span data-tippy-content="' + shared.escape(record.last_error) + '">failed at ' +
                this.whenText(record.last_delivery_at) + '</span>';
        }

        return '<span class="status-dot status-dot-pass"></span>delivered at ' + this.whenText(record.last_delivery_at);
    },

    renderDestinations: function() {
        var pane = document.getElementById('notify-destinations');
        var self = this;

        if (notifyModel.rulesetId === null) {
            pane.innerHTML = '<div class="test-run-note">No ruleset is stored yet - destinations attach to rulesets.</div>';
            return;
        }

        var html = '<div class="test-grid-title">Who gets told</div>';

        if (notifyModel.destinations.length === 0) {
            html += '<div class="test-run-note">Nobody hears about this ruleset yet. Pick a platform and a ' +
                'channel below - every event in the matrix will be delivered there.</div>';
        } else {
            html += '<table class="test-grid notify-grid"><thead><tr>' +
                '<th>Platform</th><th>Target</th><th>Last delivery</th><th>Added by</th><th></th>' +
                '</tr></thead><tbody>';

            notifyModel.destinations.forEach(function(record) {
                html += '<tr>' +
                    '<td class="test-label-cell notify-kind-cell">' +
                        shared.escape(notifyModel.config.kindLabels[record.kind]) + '</td>' +
                    '<td class="test-value-cell notify-target-cell">' + shared.escape(record.target) + '</td>' +
                    '<td class="notify-status-cell">' + self.statusHtml(record) + '</td>' +
                    '<td class="notify-author-cell">' + shared.escape(record.created_by) + '</td>' +
                    '<td class="notify-delete-cell"><button class="button-mini button-mini-danger" ' +
                        'onclick="notifyView.deleteDestination(' + record.id + ')">Remove</button></td>' +
                    '</tr>';
            });

            html += '</tbody></table>';
        }

        html += this.addRowHtml();
        pane.innerHTML = html;
    },

    addRowHtml: function() {
        var html = '<div class="notify-add-row">' +
            '<select class="notify-select" id="notify-add-kind" onchange="notifyView.setAddKind(this)">';

        html += '<option value=""' + (this.addKind === null ? ' selected' : '') + '>Platform...</option>';
        notifyModel.config.kinds.forEach(function(kind) {
            var selected = kind === notifyView.addKind ? ' selected' : '';
            html += '<option value="' + kind + '"' + selected + '>' +
                shared.escape(notifyModel.config.kindLabels[kind]) + '</option>';
        });
        html += '</select>';

        html += '<select class="notify-select notify-target-select" id="notify-add-target">';

        if (this.isLoadingTargets) {
            html += '<option value="">Loading</option>';
        } else if (this.addKind === null) {
            html += '<option value="">Pick the platform first</option>';
        } else if (notifyModel.targets.length === 0) {
            html += '<option value="">The platform offers no channels</option>';
        } else {
            notifyModel.targets.forEach(function(entry) {
                html += '<option value="' + shared.escape(entry.target) + '">' + shared.escape(entry.name) + '</option>';
            });
        }

        html += '</select>';
        html += '<button class="button-ghost" onclick="notifyView.addDestination(this)">Add destination</button>';
        html += '</div>';
        return html;
    },

// ////////////////////////////////////////////////////////////////////////

    renderCredentials: function() {
        var pane = document.getElementById('notify-credentials-pane');
        if (pane === null) { return; }

        var html = '<div class="test-grid-title">Chat credentials</div>';

        notifyModel.credentials.forEach(function(entry) {
            var kind = entry.kind;
            var label = notifyModel.config.kindLabels[kind];

            html += '<div class="notify-card">';
            html += '<div class="notify-card-title">' + shared.escape(label) + '</div>';

            if (entry.is_configured) {
                html += '<div class="notify-card-status"><span class="status-dot status-dot-pass"></span>' +
                    'Configured by ' + shared.escape(entry.updated_by) + ' at ' +
                    notifyView.whenText(entry.updated_at) + '.</div>';
            } else {
                html += '<div class="notify-card-status"><span class="status-dot status-dot-information"></span>' +
                    shared.escape(label) + ' is not configured.</div>';
            }

            notifyModel.config.credentialFields[kind].forEach(function(field) {
                html += '<div class="notify-field-row"><label>' + shared.escape(field.label) + '</label>' +
                    '<input type="password" id="notify-field-' + kind + '-' + field.name + '" ' +
                    'autocomplete="off"></div>';
            });

            html += '<div class="notify-card-actions">' +
                '<button class="button-ghost" onclick="notifyView.saveCredentials(this, \'' + kind + '\')">Save</button>' +
                '</div>';

            if (entry.is_configured) {
                html += '<div class="notify-test-row">' +
                    '<input type="text" id="notify-test-' + kind + '" placeholder="Channel to test against...">' +
                    '<button class="button-ghost" onclick="notifyView.sendTest(this, \'' + kind + '\')" ' +
                    'data-tippy-content="Sends one test message there with the stored credentials - the ' +
                    'platform\u2019s own answer comes back verbatim when it refuses.">Send test</button>' +
                    '</div>';
            }

            html += '</div>';
        });

        pane.innerHTML = html;
    },

// ////////////////////////////////////////////////////////////////////////

    renderProblems: function() {
        var head = document.getElementById('problems-head');
        var list = document.getElementById('problems-list');
        var items = [];
        var problemCount = 0;

        notifyModel.destinations.forEach(function(record) {
            if (record.last_status !== 'error') { return; }
            problemCount += 1;
            items.push('<div class="problem-item"><span class="status-dot status-dot-error"></span>' +
                '<span>Delivery to ' + shared.escape(record.target) + ' over ' +
                shared.escape(notifyModel.config.kindLabels[record.kind]) + ' failed: ' +
                shared.escape(record.last_error) + '</span></div>');
        });

        notifyModel.unconfiguredKindsInUse().forEach(function(kind) {
            problemCount += 1;
            items.push('<div class="problem-item"><span class="status-dot status-dot-warning"></span>' +
                '<span>Destinations use ' + shared.escape(notifyModel.config.kindLabels[kind]) +
                ' but no ' + shared.escape(notifyModel.config.kindLabels[kind]) +
                ' credentials are stored.</span></div>');
        });

        head.textContent = 'Problems (' + problemCount + ')';
        if (items.length === 0) {
            list.innerHTML = '<div class="problem-item problem-none">No problems.</div>';
            return;
        }
        list.innerHTML = items.join('');
    },
};

window.notifyView = notifyView;

})();
