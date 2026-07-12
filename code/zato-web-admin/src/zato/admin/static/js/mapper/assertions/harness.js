
// Mapper - the browser assertion harness.
// Runs on test.html and writes one list item per assertion plus a
// summary line, so an external test runner can read the results.
// The suites themselves live in the other assertions/ files, each
// running at load - the last one to finish calls finish().

(function($) {

    zato.mapper.assertions = {};

    var results = document.getElementById('assertion-results');
    var summary = document.getElementById('assertion-summary');
    var passedCount = 0;
    var failedCount = 0;

    zato.mapper.assertions.storageKey = 'zato-mapper-artifact-assertions';

// ////////////////////////////////////////////////////////////////////////

    function record(name, isOk) {
        var item = document.createElement('li');
        item.className = isOk ? 'assertion-pass' : 'assertion-fail';
        item.textContent = (isOk ? 'pass' : 'fail') + ': ' + name;
        results.appendChild(item);

        if (isOk) {
            passedCount += 1;
        }
        else {
            failedCount += 1;
        }
    }

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.assertions.check = function(name, condition) {
        record(name, condition === true);
    };

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.assertions.checkEqual = function(name, actual, expected) {
        var isOk = actual === expected;
        if (isOk) {
            record(name, true);
        }
        else {
            record(name + ' - expected `' + expected + '` but found `' + actual + '`', false);
        }
    };

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.assertions.findRecord = function(records, code) {
        for (var recordIdx = 0; recordIdx < records.length; recordIdx++) {
            if (records[recordIdx].code === code) {
                return records[recordIdx];
            }
        }

        return null;
    };

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.assertions.makeRow = function(target, expression, condition) {

        var out = zato.mapper.store.newMapping();
        out.target = target;
        out.expression = expression;
        out.condition = condition;

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.assertions.fieldByName = function(node, name) {
        for (var fieldIdx = 0; fieldIdx < node.fields.length; fieldIdx++) {
            if (node.fields[fieldIdx].name === name) {
                return node.fields[fieldIdx];
            }
        }

        return null;
    };

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.assertions.finish = function() {
        summary.textContent = passedCount + ' passed, ' + failedCount + ' failed';
        summary.setAttribute('data-complete', 'true');
        summary.setAttribute('data-passed', passedCount);
        summary.setAttribute('data-failed', failedCount);
    };

})(jQuery);
