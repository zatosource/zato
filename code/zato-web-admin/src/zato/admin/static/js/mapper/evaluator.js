
// Mapper kit - the preview evaluator.
// Builds the output document from the artifact against one source
// payload, entirely in the browser. Evaluation order is defined:
// top-level rows in list order, then scopes in list order with their
// child rows per element, conditions always before expressions.
// Errors never wipe anything - each failing row carries its own error
// with the input it saw, and every other row still evaluates.

(function($) {

    zato.mapper.evaluator = {};

// ////////////////////////////////////////////////////////////////////////

    function isEmpty(value) {

        var out = value === undefined || value === null || value === '';
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Writes a value into the output object at a dotted path,
    // creating intermediate objects along the way.
    function setPath(output, path, value) {

        var parts = path.split('.');
        var current = output;

        for (var partIdx = 0; partIdx < parts.length - 1; partIdx++) {
            var part = parts[partIdx];
            if (current[part] === undefined) {
                current[part] = {};
            }
            current = current[part];
        }

        current[parts[parts.length - 1]] = value;
    }

// ////////////////////////////////////////////////////////////////////////

    // Evaluates one row against one input context.
    // Returns {value, error, skipped, omitted, written}.
    async function evaluateRow(row, context) {

        var result = {value: undefined, error: '', skipped: false, omitted: false, written: false};

        // A row without an expression has nothing to evaluate yet -
        // it is still being filled in, which is not an error.
        if (row.expression === '') {
            return result;
        }

        // The condition decides whether the row runs at all ..
        if (row.condition !== '') {
            try {
                var conditionExpression = jsonata(row.condition);
                var conditionValue = await conditionExpression.evaluate(context);
                if (!conditionValue) {
                    result.skipped = true;
                    return result;
                }
            } catch(error) {
                result.error = error.message;
                return result;
            }
        }

        // .. then the expression produces the value ..
        try {
            var expression = jsonata(row.expression);
            result.value = await expression.evaluate(context);
        } catch(error) {
            result.error = error.message;
            return result;
        }

        // .. an empty result takes the row's default when one is set ..
        if (isEmpty(result.value)) {
            if (row['default'] !== null) {
                result.value = row['default'];
            }
        }

        // .. and a still-empty result is either omitted or written as-is.
        if (isEmpty(result.value)) {
            if (row.omit_if_empty) {
                result.omitted = true;
                return result;
            }
        }

        if (result.value !== undefined) {
            result.written = true;
        }

        return result;
    }

// ////////////////////////////////////////////////////////////////////////

    // Runs the whole mapping against one source payload.
    // Returns a promise of:
    //   output:  the produced document
    //   rows:    one result per top-level row, in row order
    //   scopes:  per scope: {error, length, elements: [[child row results]]}
    zato.mapper.evaluator.run = async function(artifact, payload) {

        var output = {};
        var rows = [];
        var scopes = [];

        zato.mapper.log('evaluator', 'run starts', {mappings: artifact.mappings.length, scopes: artifact.scopes.length});

        // Top-level rows first, in list order ..
        for (var rowIdx = 0; rowIdx < artifact.mappings.length; rowIdx++) {
            var row = artifact.mappings[rowIdx];
            var result = await evaluateRow(row, payload);

            if (result.written) {
                if (row.target !== '') {
                    setPath(output, row.target, result.value);
                }
            }

            zato.mapper.log('evaluator', 'row ' + rowIdx, {target: row.target, expression: row.expression, result: result});
            rows.push(result);
        }

        // .. then every scope, its elements in source order.
        for (var scopeIdx = 0; scopeIdx < artifact.scopes.length; scopeIdx++) {
            var scope = artifact.scopes[scopeIdx];
            var scopeResult = {error: '', length: 0, elements: []};

            var elements = [];
            try {
                var selector = jsonata(scope.source);
                var selected = await selector.evaluate(payload);

                // A single object still iterates as a one-element list,
                // an absent selection as an empty one.
                if (Array.isArray(selected)) {
                    elements = selected;
                }
                else if (selected !== undefined) {
                    elements = [selected];
                }
            } catch(error) {
                scopeResult.error = error.message;
            }

            scopeResult.length = elements.length;

            var outputList = [];
            for (var elementIdx = 0; elementIdx < elements.length; elementIdx++) {
                var elementOutput = {};
                var childResults = [];

                // Child rows evaluate relative to the current element.
                for (var childIdx = 0; childIdx < scope.mappings.length; childIdx++) {
                    var childRow = scope.mappings[childIdx];
                    var childResult = await evaluateRow(childRow, elements[elementIdx]);

                    if (childResult.written) {
                        if (childRow.target !== '') {
                            setPath(elementOutput, childRow.target, childResult.value);
                        }
                    }

                    childResults.push(childResult);
                }

                outputList.push(elementOutput);
                scopeResult.elements.push(childResults);
            }

            if (scopeResult.error === '') {
                if (scope.target !== '') {
                    setPath(output, scope.target, outputList);
                }
            }

            zato.mapper.log('evaluator', 'scope ' + scopeIdx, {target: scope.target, source: scope.source, elements: scopeResult.length, error: scopeResult.error});
            scopes.push(scopeResult);
        }

        zato.mapper.log('evaluator', 'run finished', {output: output});

        var out = {output: output, rows: rows, scopes: scopes};
        return out;
    };

})(jQuery);
