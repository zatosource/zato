'use strict';

(function() {

// ////////////////////////////////////////////////////////////////////////

editorModel.adoptedType = function(nodes) {
    var first = nodes[0];
    if (first !== undefined && first.kind !== 'reference') {
        if (typeof first.value === 'number') { return 'number'; }
        if (first.value === true || first.value === false) { return 'yes/no'; }
    }
    return 'text';
};

editorModel.adoptTerm = function(path, nodes) {
    if (vocabulary.isDeclared(path) || vocabulary.adopted[path] !== undefined) { return; }

    vocabulary.adopted[path] = {
        name: path,
        type: this.adoptedType(nodes),
        phrase: path,
        setPhrase: 'set ' + path + ' to',
        status: '',
    };
};

editorModel.adoptRuleTerms = function() {
    var self = this;

    Object.keys(this.documents).forEach(function(key) {
        var document = self.documents[key];

        document.conditions.forEach(function(condition) {
            self.adoptTerm(condition.subject, condition.values);
            condition.values.forEach(function(node) {
                if (node.kind === 'reference') { self.adoptTerm(node.term, []); }
            });
        });

        document.then.concat(document['else']).forEach(function(action) {
            self.adoptTerm(action.target, [action.value]);
            if (action.value.kind === 'reference') { self.adoptTerm(action.value.term, []); }
        });
    });
};

// ////////////////////////////////////////////////////////////////////////

editorModel.isNumber = function(value) {
    var out = /^-?\d+(?:\.\d+)?$/.test(value);
    return out;
};

editorModel.suggestChoice = function(attribute, typed) {
    var lower = typed.toLowerCase();

    var out = null;
    attribute.values.forEach(function(value) {
        if (out === null && value.toLowerCase() === lower) { out = value; }
    });

    if (out === null) {
        var bestLength = 0;
        attribute.values.forEach(function(value) {
            var valueLower = value.toLowerCase();
            var sharedLength = 0;
            while (sharedLength < lower.length && sharedLength < valueLower.length &&
                   lower[sharedLength] === valueLower[sharedLength]) {
                sharedLength += 1;
            }
            if (sharedLength > bestLength) { bestLength = sharedLength; out = value; }
        });
    }

    if (out === null) { out = attribute.values[0]; }

    return out;
};

// ////////////////////////////////////////////////////////////////////////

editorModel.isNumericType = function(attribute) {
    var out = attribute.type === 'number' || attribute.type === 'number range';
    return out;
};

editorModel.checkTypedValue = function(attribute, value, values, valueIndex, position, problems, invalidKeys, invalidKey) {
    if (attribute.type === 'choice') {
        if (attribute.values.indexOf(value) === -1) {
            invalidKeys[invalidKey] = true;
            var suggestion = this.suggestChoice(attribute, value);
            problems.push({severity: 'error',
                text: '"' + value + '" is not a known value of ' + attribute.phrase +
                    '. Known values: ' + attribute.values.join(', ') + '.',
                fix: {values: values, valueIndex: valueIndex, value: suggestion}});
        }
        return;
    }

    if (this.isNumericType(attribute) && !this.isNumber(value)) {
        invalidKeys[invalidKey] = true;
        var cleaned = value.replace(/[^0-9.\-]/g, '');
        var fix = cleaned === '' ? undefined : {values: values, valueIndex: valueIndex, value: cleaned};
        problems.push({severity: 'error',
            text: '"' + value + '" is not a number, expected something like 740 in ' + position + '.',
            fix: fix});
    }
};

editorModel.buildProblems = function() {
    var self = this;
    var problems = [];
    var invalidKeys = {};

    this.rule.conditions.forEach(function(condition, conditionIndex) {
        var position = 'condition ' + (conditionIndex + 1);

        if (condition.subject === null) {
            problems.push({severity: 'information', text: 'The rule is unfinished: pick a property in ' + position + '.'});
            return;
        }
        var attribute = vocabulary.attribute(condition.subject);

        if (condition.comparator === null) {
            problems.push({severity: 'information', text: 'The rule is unfinished: pick how to compare ' +
                attribute.phrase + ' in ' + position + '.'});
            return;
        }

        var slots = self.valueSlots(condition.comparator);
        if (slots === -1 && condition.values.length === 0) {
            problems.push({severity: 'information', text: 'The rule is unfinished: pick one or more values for ' +
                attribute.phrase + ' in ' + position + '.'});
            return;
        }

        condition.values.forEach(function(value, valueIndex) {
            if (value === '') {
                problems.push({severity: 'information', text: 'The rule is unfinished: a value is missing in ' + position + '.'});
                return;
            }
            self.checkTypedValue(attribute, value, condition.values, valueIndex, position,
                problems, invalidKeys, 'condition-' + conditionIndex + '-' + valueIndex);
        });
    });

    ['thenActions', 'elseActions'].forEach(function(listName) {
        var partName = listName === 'thenActions' ? 'the then part' : 'the else part';
        self.rule[listName].forEach(function(action, actionIndex) {
            if (action.target === null) {
                problems.push({severity: 'information', text: 'The rule is unfinished: pick an action in ' + partName + '.'});
                return;
            }
            var attribute = vocabulary.attribute(action.target);
            if (attribute.type === 'yes/no') { return; }

            var value = action.values[0];
            if (value === '') {
                problems.push({severity: 'information', text: 'The rule is unfinished: set ' +
                    attribute.phrase + ' needs a value in ' + partName + '.'});
                return;
            }
            self.checkTypedValue(attribute, value, action.values, 0, partName,
                problems, invalidKeys, listName + '-' + actionIndex + '-0');
        });
    });

    var out = {problems: problems, invalidKeys: invalidKeys};
    return out;
};

editorModel.serverProblems = function() {
    var out = this.serverErrors.map(function(error) {

        // The place reads the way an IDE would say it - the line first, the
        // block after it only when the server named one
        var where = [];
        if (error.line > 0) { where.push('Line ' + error.line); }
        if (error.block !== '') { where.push('in the ' + error.block + ' block'); }

        // The server's messages point at the offending text with an arrow -
        // on screen that reads as plain punctuation
        var text = error.message.split(' -> ').join(': ');

        if (where.length > 0) {
            var place = where.join(', ');
            text = place.charAt(0).toUpperCase() + place.slice(1) + ': ' + text;
        }

        var problem = {severity: error.severity, text: text};
        return problem;
    });
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})();
