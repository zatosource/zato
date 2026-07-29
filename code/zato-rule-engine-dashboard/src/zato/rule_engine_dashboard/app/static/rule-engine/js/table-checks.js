'use strict';

(function() {

var tableModel = window.tableModel;

// ////////////////////////////////////////////////////////////////////////

tableModel.errorLabel = function(error) {
    var match = /^column_(.+)$/.exec(error.rule);
    if (match === null) { return ''; }

    var out = match[1] === '0' ? 'Base' : match[1];
    return out;
};

tableModel.invalidCells = function() {
    var self = this;
    var out = [];

    this.serverErrors.forEach(function(error) {
        var label = self.errorLabel(error);
        if (label === '' || error.field === '') { return; }
        out.push({column: label, row: error.field});
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tableModel.conflictLabels = function() {
    var out = [];
    if (this.conflictResult === null) { return out; }

    this.conflictResult.conflicts.forEach(function(pair) {
        out.push(String(pair.first));
        out.push(String(pair.second));
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tableModel.ruleName = function(label) {
    var out = label === 'Base' ? 'the Base column' : 'rule ' + label;
    return out;
};

tableModel.buildProblems = function() {
    var self = this;
    var out = [];

    this.serverErrors.forEach(function(error) {
        var label = self.errorLabel(error);
        var where = label === '' ? 'the table' : self.ruleName(label);
        out.push({severity: 'error', text: error.message + ' (in ' + where + ')', column: label});
    });

    if (this.conflictResult !== null) {
        this.conflictResult.conflicts.forEach(function(pair) {
            out.push({severity: 'error', text: 'Rules ' + pair.first + ' and ' + pair.second +
                ' can fire on the same data with different values for ' + pair.targets.join(', ') +
                '. Change an action or declare an override.', column: String(pair.second)});
        });

        this.conflictResult.overridden.forEach(function(pair) {
            out.push({severity: 'information', text: 'Rules ' + pair.winner + ' and ' + pair.loser +
                ' overlap, the declared override resolves it: rule ' + pair.winner + ' wins.',
                column: String(pair.winner)});
        });

        this.conflictResult.unknown_overrides.forEach(function(entry) {
            out.push({severity: 'error', text: 'Rule ' + entry.column + ' declares an override of column ' +
                entry.overrides + ', which does not exist.', column: String(entry.column)});
        });
    }

    this.subsumption.forEach(function(pair) {
        out.push({severity: 'warning', text: 'Rule ' + pair.general + ' already covers rule ' + pair.specific +
            ': everything rule ' + pair.specific + ' matches, rule ' + pair.general + ' matches too.',
            column: String(pair.specific)});
    });

    this.unreachable.forEach(function(entry) {
        out.push({severity: 'warning', text: 'Rule ' + entry.column + ' can never fire: its conditions on ' +
            entry.subject + ' contradict each other.', column: String(entry.column)});
    });

    this.table.columns.forEach(function(column) {
        var label = self.label(column);
        if (self.generatedNumbers[label] !== true) { return; }

        if (Object.keys(column.actions).length === 0) {
            out.push({severity: 'warning', text: 'Rule ' + label +
                ' was added by the completeness check. Its actions are empty and yours to fill in.', column: label});
        }
    });

    return out;
};

// ////////////////////////////////////////////////////////////////////////

tableModel.check = function(onDone, onError) {
    var self = this;

    data.post(this.config.urls.validate, {table: this.table}, function(payload) {
        self.serverErrors = payload.errors;
        self.readings = payload.readings;
        onDone();
    }, onError);
};

tableModel.withValidTable = function(onValid, onError) {
    var self = this;

    this.check(function() {
        if (self.serverErrors.length > 0) {
            onError(self.config.structuralProblemsMessage);
            return;
        }
        onValid();
    }, onError);
};

tableModel.runChecks = function(onDone, onError) {
    var self = this;

    this.withValidTable(function() {
        data.post(self.config.urls.checks, {table: self.table}, onDone, onError);
    }, onError);
};

})();
