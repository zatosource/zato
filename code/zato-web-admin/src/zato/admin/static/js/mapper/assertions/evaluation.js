
// Mapper - browser assertions for the expression builder model and
// the preview evaluator. The evaluator suite is asynchronous, so this
// file is the one that calls finish() once everything has run.

(function($) {

    var check = zato.mapper.assertions.check;
    var checkEqual = zato.mapper.assertions.checkEqual;
    var makeRow = zato.mapper.assertions.makeRow;

// ////////////////////////////////////////////////////////////////////////
// The expression builder model
// ////////////////////////////////////////////////////////////////////////

    function runBuilderAssertions() {

        // The common shape parses into tokens ..
        var parsed = zato.mapper.builder.parse('quantity * unit_price');
        check('an operand-operator sequence parses', parsed.ok === true);
        checkEqual('the parsed tokens keep their order', parsed.tokens.length, 3);
        checkEqual('the first token is the first operand', parsed.tokens[0].value, 'quantity');
        checkEqual('the middle token is the operator', parsed.tokens[1].value, '*');

        // .. a wrapping function is recognized ..
        var wrapped = zato.mapper.builder.parse('$uppercase(customer)');
        check('a wrapping function parses', wrapped.ok === true);
        checkEqual('the wrapping function is kept', wrapped.wrap, '$uppercase');

        // .. serializing the model reproduces the expression ..
        checkEqual('serializing reproduces the expression', zato.mapper.builder.serialize(parsed), 'quantity * unit_price');
        checkEqual('serializing keeps the wrapping function', zato.mapper.builder.serialize(wrapped), '$uppercase(customer)');

        // .. and anything beyond the covered shape stays raw.
        check('a lambda stays raw', zato.mapper.builder.parse('$map(lines, function($v) { $v.sku })').ok === false);
        check('a trailing operator stays raw', zato.mapper.builder.parse('quantity *').ok === false);
        check('an empty expression is buildable', zato.mapper.builder.parse('').ok === true);
    }

// ////////////////////////////////////////////////////////////////////////
// The preview evaluator
// ////////////////////////////////////////////////////////////////////////

    async function runEvaluatorAssertions() {

        var payload = {
            customer: 'ACME',
            quantity: 2,
            unit_price: 10.5,
            notes: '',
            lines: [
                {sku: 'AA-11', quantity: 2},
                {sku: 'BB-22', quantity: 5}
            ]
        };

        var artifact = zato.mapper.store.newArtifact();
        artifact.mappings.push(makeRow('invoice.customer', 'customer', ''));
        artifact.mappings.push(makeRow('invoice.total', 'quantity * unit_price', ''));

        var results = await zato.mapper.evaluator.run(artifact, payload);

        checkEqual('a row evaluates against the payload', results.rows[0].value, 'ACME');
        checkEqual('an arithmetic expression evaluates', results.rows[1].value, 21);
        checkEqual('the output nests dotted targets', results.output.invoice.customer, 'ACME');
        checkEqual('the output carries the computed value', results.output.invoice.total, 21);

        // A false condition skips the row.
        var conditional = zato.mapper.store.newArtifact();
        conditional.mappings.push(makeRow('flag', 'customer', 'quantity > 100'));
        var conditionalResults = await zato.mapper.evaluator.run(conditional, payload);
        check('a false condition skips the row', conditionalResults.rows[0].skipped === true);
        check('a skipped row writes nothing', conditionalResults.output.flag === undefined);

        // An empty value takes the row's default when one is set.
        var defaulted = zato.mapper.store.newArtifact();
        var defaultedRow = makeRow('notes', 'notes', '');
        defaultedRow['default'] = 'No notes';
        defaulted.mappings.push(defaultedRow);
        var defaultedResults = await zato.mapper.evaluator.run(defaulted, payload);
        checkEqual('an empty value takes the default', defaultedResults.output.notes, 'No notes');

        // The omit flag drops a still-empty value from the output.
        var omitted = zato.mapper.store.newArtifact();
        var omittedRow = makeRow('notes', 'notes', '');
        omittedRow.omit_if_empty = true;
        omitted.mappings.push(omittedRow);
        var omittedResults = await zato.mapper.evaluator.run(omitted, payload);
        check('an empty value with the omit flag is omitted', omittedResults.rows[0].omitted === true);
        check('an omitted row writes nothing', omittedResults.output.notes === undefined);

        // A broken expression carries its own error, other rows still run.
        var broken = zato.mapper.store.newArtifact();
        broken.mappings.push(makeRow('first', '$number(customer)', ''));
        broken.mappings.push(makeRow('second', 'customer', ''));
        var brokenResults = await zato.mapper.evaluator.run(broken, payload);
        check('a failing row carries its own error', brokenResults.rows[0].error !== '');
        checkEqual('other rows still evaluate', brokenResults.rows[1].value, 'ACME');

        // A scope maps every element of the selected list.
        var scoped = zato.mapper.store.newArtifact();
        scoped.scopes.push({
            target: 'invoice.items',
            source: 'lines',
            mappings: [makeRow('code', 'sku', ''), makeRow('amount', 'quantity * 2', '')]
        });
        var scopedResults = await zato.mapper.evaluator.run(scoped, payload);
        checkEqual('a scope iterates every element', scopedResults.output.invoice.items.length, 2);
        checkEqual('child rows evaluate relative to their element', scopedResults.output.invoice.items[1].code, 'BB-22');
        checkEqual('child rows compute per element', scopedResults.output.invoice.items[1].amount, 10);
        checkEqual('per-element results are kept for preview', scopedResults.scopes[0].elements[0][0].value, 'AA-11');
    }

// ////////////////////////////////////////////////////////////////////////

    runBuilderAssertions();

    // The evaluator suite is asynchronous - the summary waits for it.
    var evaluatorRun = runEvaluatorAssertions();
    evaluatorRun.then(zato.mapper.assertions.finish);

})(jQuery);
