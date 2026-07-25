'use strict';

// The problems feed for the decision table: the server's structural
// errors, the on-demand conflict, subsumption and unreachable findings,
// the completeness proposals, and the calls that run those checks on
// the server. Augments the tableModel namespace, no DOM access here.

(function() {

var tableModel = window.tableModel;

// ////////////////////////////////////////////////////////////////////////

// The column label a structural error points at, from its rule name
// like column_3, or blank for table-wide errors
tableModel.errorLabel = function(error) {
    var match = /^column_(.+)$/.exec(error.rule);
    if (match === null) { return ''; }

    var out = match[1] === '0' ? 'Base' : match[1];
    return out;
};

// The cells the last validation flagged, for the red shading
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

// The columns the last conflict check flagged, for the red shading
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

// A label like '3' spoken as 'rule 3', the Base column spoken by name
tableModel.ruleName = function(label) {
    var out = label === 'Base' ? 'the Base column' : 'rule ' + label;
    return out;
};

tableModel.buildProblems = function() {
    var self = this;
    var out = [];

    // The server's structural errors come first, each tied to its column
    this.serverErrors.forEach(function(error) {
        var label = self.errorLabel(error);
        var where = label === '' ? 'the table' : self.ruleName(label);
        out.push({severity: 'error', text: error.message + ' (in ' + where + ')', column: label});
    });

    // The on-demand conflict check: unresolved pairs, resolved overrides
    // and overrides that point at columns that do not exist
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

    // Subsumption is always a warning - a narrower column under a more
    // general one is a problem waiting to surface in a bigger table
    this.subsumption.forEach(function(pair) {
        out.push({severity: 'warning', text: 'Rule ' + pair.general + ' already covers rule ' + pair.specific +
            ': everything rule ' + pair.specific + ' matches, rule ' + pair.general + ' matches too.',
            column: String(pair.specific)});
    });

    // Unreachable columns can never fire, their own conditions contradict
    this.unreachable.forEach(function(entry) {
        out.push({severity: 'warning', text: 'Rule ' + entry.column + ' can never fire: its conditions on ' +
            entry.subject + ' contradict each other.', column: String(entry.column)});
    });

    // Columns the completeness check proposed still wait for their actions
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

// The server parses every cell and answers with structural errors
// shaped like the rule parser's
tableModel.check = function(onDone) {
    var self = this;

    data.post(this.config.urls.validate, {table: this.table}, function(payload) {
        self.serverErrors = payload.errors;
        onDone();
    }, data.reportError);
};

// The checks, expand and compress endpoints answer a structurally
// broken table with the validation findings, so the validation runs
// first and its findings land in the problems panel instead
tableModel.withValidTable = function(onValid, onError) {
    var self = this;

    this.check(function() {
        if (self.serverErrors.length > 0) {
            onError(self.config.structuralProblemsMessage);
            return;
        }
        onValid();
    });
};

// The four integrity checks in one server answer
tableModel.runChecks = function(onDone, onError) {
    var self = this;

    this.withValidTable(function() {
        data.post(self.config.urls.checks, {table: self.table}, onDone, onError);
    }, onError);
};

})();
