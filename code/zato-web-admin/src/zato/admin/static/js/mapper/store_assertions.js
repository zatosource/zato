
// Mapper - browser assertions for the store and the schema module.
// Runs on test.html and writes one list item per assertion plus a
// summary line, so an external test runner can read the results.

(function($) {

    var results = document.getElementById('assertion-results');
    var summary = document.getElementById('assertion-summary');
    var passedCount = 0;
    var failedCount = 0;

    var assertionStorageKey = 'zato-mapper-artifact-assertions';

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

    function check(name, condition) {
        record(name, condition === true);
    }

    function checkEqual(name, actual, expected) {
        var isOk = actual === expected;
        if (isOk) {
            record(name, true);
        }
        else {
            record(name + ' - expected `' + expected + '` but found `' + actual + '`', false);
        }
    }

// ////////////////////////////////////////////////////////////////////////
// Artifact shape and deterministic serialization
// ////////////////////////////////////////////////////////////////////////

    function runArtifactAssertions() {

        var artifact = zato.mapper.store.newArtifact();

        checkEqual('new artifact carries the current format version', artifact.version, zato.mapper.config.artifactVersion);
        checkEqual('new artifact has the default name', artifact.name, zato.mapper.config.defaultName);
        check('new artifact has no source schema tree', artifact.source_schema.root === null);
        check('new artifact has no target schema tree', artifact.target_schema.root === null);
        checkEqual('new artifact has no mappings', artifact.mappings.length, 0);

        // Serialization is deterministic - two runs are byte-identical ..
        var first = zato.mapper.store.serialize(artifact);
        var second = zato.mapper.store.serialize(artifact);
        checkEqual('serializing twice produces identical text', first, second);

        // .. a parse and re-serialize round trip is also byte-identical ..
        var roundTrip = zato.mapper.store.serialize(JSON.parse(first));
        checkEqual('a parse and re-serialize round trip is identical', roundTrip, first);

        // .. and the top-level keys appear in the documented order.
        check('version serializes before name', first.indexOf('"version"') < first.indexOf('"name"'));
        check('name serializes before source_schema', first.indexOf('"name"') < first.indexOf('"source_schema"'));
        check('source_schema serializes before target_schema', first.indexOf('"source_schema"') < first.indexOf('"target_schema"'));
        check('target_schema serializes before mappings', first.indexOf('"target_schema"') < first.indexOf('"mappings"'));
        check('mappings serializes before samples', first.indexOf('"mappings"') < first.indexOf('"samples"'));

        // A mapping row always serializes all of its keys.
        var row = zato.mapper.store.newMapping();
        row.target = 'invoice.total';
        row.expression = 'order.total';
        artifact.mappings.push(row);

        var withRow = zato.mapper.store.serialize(artifact);
        check('a mapping row serializes its condition key even when empty', withRow.indexOf('"condition"') > -1);
        check('a mapping row serializes its origin key even when empty', withRow.indexOf('"origin"') > -1);
        check('a mapping row serializes its default key even when unset', withRow.indexOf('"default"') > -1);
        check('a mapping row serializes its omit flag', withRow.indexOf('"omit_if_empty"') > -1);

        // The row factory produces the canonical shape.
        var fresh = zato.mapper.store.newMapping();
        check('a new row has no default', fresh['default'] === null);
        check('a new row does not omit empty values', fresh.omit_if_empty === false);
    }

// ////////////////////////////////////////////////////////////////////////
// Validation
// ////////////////////////////////////////////////////////////////////////

    function findRecord(records, code) {
        for (var recordIdx = 0; recordIdx < records.length; recordIdx++) {
            if (records[recordIdx].code === code) {
                return records[recordIdx];
            }
        }

        return null;
    }

    function makeRow(target, expression, condition) {

        var out = zato.mapper.store.newMapping();
        out.target = target;
        out.expression = expression;
        out.condition = condition;

        return out;
    }

    function runValidationAssertions() {

        var artifact = zato.mapper.store.newArtifact();
        checkEqual('a new artifact validates clean', zato.mapper.store.validate(artifact).length, 0);

        // An unsupported version is loud.
        var badVersion = zato.mapper.store.newArtifact();
        badVersion.version = 999;
        check('an unsupported version is reported', findRecord(zato.mapper.store.validate(badVersion), 'artifact-version') !== null);

        // An empty name is loud.
        var badName = zato.mapper.store.newArtifact();
        badName.name = '';
        check('an empty name is reported', findRecord(zato.mapper.store.validate(badName), 'artifact-name') !== null);

        // A mapping without a target is loud.
        var badTarget = zato.mapper.store.newArtifact();
        badTarget.mappings.push(makeRow('', 'order.total', ''));
        check('a mapping without a target is reported', findRecord(zato.mapper.store.validate(badTarget), 'mapping-target') !== null);

        // An expression that does not parse is loud.
        var badExpression = zato.mapper.store.newArtifact();
        badExpression.mappings.push(makeRow('invoice.total', 'order.total +', ''));
        check('an unparseable expression is reported', findRecord(zato.mapper.store.validate(badExpression), 'mapping-expression-parse') !== null);

        // A condition that does not parse is loud, a valid one is not.
        var badCondition = zato.mapper.store.newArtifact();
        badCondition.mappings.push(makeRow('invoice.total', 'order.total', 'order.total >'));
        check('an unparseable condition is reported', findRecord(zato.mapper.store.validate(badCondition), 'mapping-condition-parse') !== null);

        var goodCondition = zato.mapper.store.newArtifact();
        goodCondition.mappings.push(makeRow('invoice.total', 'order.total', 'order.total > 0'));
        checkEqual('a valid condition validates clean', zato.mapper.store.validate(goodCondition).length, 0);

        // A sample with an unknown side is loud.
        var badSample = zato.mapper.store.newArtifact();
        badSample.samples.push({name: 'order-example', side: 'sideways', payload: {}});
        check('a sample with an unknown side is reported', findRecord(zato.mapper.store.validate(badSample), 'sample-side') !== null);

        // A scope without a source selector is loud.
        var badScope = zato.mapper.store.newArtifact();
        badScope.scopes.push({target: 'invoice.lines', source: '', mappings: []});
        check('a scope without a source selector is reported', findRecord(zato.mapper.store.validate(badScope), 'scope-source') !== null);

        // A non-boolean omit flag is loud.
        var badOmit = zato.mapper.store.newArtifact();
        var badOmitRow = makeRow('invoice.total', 'order.total', '');
        badOmitRow.omit_if_empty = 'yes';
        badOmit.mappings.push(badOmitRow);
        check('a non-boolean omit flag is reported', findRecord(zato.mapper.store.validate(badOmit), 'mapping-omit-flag') !== null);

        // A duplicate field name in a schema is loud.
        var badSchema = zato.mapper.store.newArtifact();
        var duplicateRoot = zato.mapper.schema.newObjectNode();
        duplicateRoot.fields.push({name: 'customer', optional: false, node: zato.mapper.schema.newLeafNode(['string'], '')});
        duplicateRoot.fields.push({name: 'customer', optional: false, node: zato.mapper.schema.newLeafNode(['string'], '')});
        badSchema.source_schema.root = duplicateRoot;
        check('a duplicate schema field name is reported', findRecord(zato.mapper.store.validate(badSchema), 'schema-field-duplicate') !== null);
    }

// ////////////////////////////////////////////////////////////////////////
// The store instance - mutations, undo and redo, autosave
// ////////////////////////////////////////////////////////////////////////

    function runStoreInstanceAssertions() {

        // Start from a clean slate in browser storage.
        window.store.remove(assertionStorageKey);

        var store = zato.mapper.store.create({storageKey: assertionStorageKey});
        checkEqual('a fresh store starts with the default name', store.getArtifact().name, zato.mapper.config.defaultName);
        check('a fresh store has nothing to undo', store.canUndo() === false);
        check('a fresh store has nothing to redo', store.canRedo() === false);

        // A mutation changes the artifact and autosaves it.
        store.setName('Order to invoice');
        checkEqual('setName changes the artifact name', store.getArtifact().name, 'Order to invoice');
        check('a mutation autosaves to browser storage', window.store.get(assertionStorageKey).indexOf('Order to invoice') > -1);
        check('a mutation makes undo available', store.canUndo() === true);

        // Undo restores the previous state, redo brings the change back.
        store.undo();
        checkEqual('undo restores the previous name', store.getArtifact().name, zato.mapper.config.defaultName);
        check('undo makes redo available', store.canRedo() === true);

        store.redo();
        checkEqual('redo brings the change back', store.getArtifact().name, 'Order to invoice');

        // A new mutation clears the redo stack.
        store.undo();
        store.setName('Order to shipment');
        check('a new mutation clears the redo stack', store.canRedo() === false);

        // Schema mutations are undoable like any other.
        var root = zato.mapper.schema.inferFromExample({customer: 'ACME', total: 125.5});
        store.setSchemaRoot('source', root);
        check('setSchemaRoot stores the tree', store.getArtifact().source_schema.root !== null);

        store.undo();
        check('undo removes the schema tree again', store.getArtifact().source_schema.root === null);
        store.redo();

        // The autosaved artifact is restored by a new store instance.
        var restored = zato.mapper.store.create({storageKey: assertionStorageKey});
        checkEqual('a new store instance restores the autosaved name', restored.getArtifact().name, 'Order to shipment');
        check('a new store instance restores the autosaved schema', restored.getArtifact().source_schema.root !== null);

        // Loading an invalid artifact is rejected and changes nothing.
        var invalid = zato.mapper.store.newArtifact();
        invalid.version = 999;
        var records = store.loadArtifact(invalid);
        check('loading an invalid artifact returns its validation records', records.length > 0);
        checkEqual('loading an invalid artifact changes nothing', store.getArtifact().name, 'Order to shipment');

        // Loading a valid artifact replaces the current one.
        var valid = zato.mapper.store.newArtifact();
        valid.name = 'Imported mapping';
        checkEqual('loading a valid artifact returns no records', store.loadArtifact(valid).length, 0);
        checkEqual('loading a valid artifact replaces the current one', store.getArtifact().name, 'Imported mapping');

        // Scope child rows can be removed one at a time ..
        store.addScope({target: 'invoice.items', source: 'lines', mappings: [makeRow('code', 'sku', '')]});
        store.removeScopeMapping(0, 0);
        checkEqual('removeScopeMapping removes the child row', store.getArtifact().scopes[0].mappings.length, 0);

        // .. and everything clears at once, undoably.
        store.addMapping(makeRow('invoice.total', 'order.total', ''));
        store.clearMappings();
        checkEqual('clearMappings removes every row', store.getArtifact().mappings.length, 0);
        checkEqual('clearMappings removes every scope', store.getArtifact().scopes.length, 0);

        store.undo();
        checkEqual('undoing clearMappings restores the rows', store.getArtifact().mappings.length, 1);
        checkEqual('undoing clearMappings restores the scopes', store.getArtifact().scopes.length, 1);

        window.store.remove(assertionStorageKey);
    }

// ////////////////////////////////////////////////////////////////////////
// Schema inference
// ////////////////////////////////////////////////////////////////////////

    function fieldByName(node, name) {
        for (var fieldIdx = 0; fieldIdx < node.fields.length; fieldIdx++) {
            if (node.fields[fieldIdx].name === name) {
                return node.fields[fieldIdx];
            }
        }

        return null;
    }

    function runInferenceAssertions() {

        var example = {
            customer: 'ACME',
            total: 125.5,
            is_priority: true,
            notes: null,
            created: '2026-05-01',
            updated: '2026-05-01T10:30:00Z',
            cutoff: '17:30:00',
            address: {city: 'Prague', street: 'Dlouha'},
            lines: [
                {sku: 'AA-11', quantity: 2},
                {sku: 'BB-22', quantity: 5, discount: 0.1}
            ],
            tags: []
        };

        var root = zato.mapper.schema.inferFromExample(example);

        checkEqual('the example infers as an object', root.kind, 'object');
        checkEqual('field order is preserved exactly', root.fields[0].name, 'customer');

        checkEqual('a string infers as a string leaf', fieldByName(root, 'customer').node.types[0], 'string');
        checkEqual('a number infers as a number leaf', fieldByName(root, 'total').node.types[0], 'number');
        checkEqual('a boolean infers as a boolean leaf', fieldByName(root, 'is_priority').node.types[0], 'boolean');
        checkEqual('a null infers as an unknown leaf', fieldByName(root, 'notes').node.types[0], 'unknown');

        checkEqual('an ISO date is tagged with a date hint', fieldByName(root, 'created').node.format, 'date');
        checkEqual('an ISO datetime is tagged with a datetime hint', fieldByName(root, 'updated').node.format, 'datetime');
        checkEqual('an ISO time is tagged with a time hint', fieldByName(root, 'cutoff').node.format, 'time');
        checkEqual('a plain string carries no format hint', fieldByName(root, 'customer').node.format, '');

        checkEqual('a nested object recurses', fieldByName(root, 'address').node.kind, 'object');

        // Array element merging - the element schema is the union of all elements.
        var lines = fieldByName(root, 'lines').node;
        checkEqual('an array of objects infers as a repeating node', lines.kind, 'array');
        check('a field present in every element is not optional', fieldByName(lines.element, 'sku').optional === false);
        check('a field absent from some elements is optional', fieldByName(lines.element, 'discount').optional === true);

        // An empty array stays unknown until refined.
        checkEqual('an empty array has an unknown element type', fieldByName(root, 'tags').node.element.types[0], 'unknown');

        // Two elements disagreeing on a scalar type produce a recorded union.
        var mixed = zato.mapper.schema.inferFromExample([{code: 'A'}, {code: 7}]);
        checkEqual('disagreeing scalar types record a union', mixed.element.fields[0].node.types.join('|'), 'string|number');

        // A second sample refines the schema - shared fields stay, new ones are optional.
        var firstSample = zato.mapper.schema.inferFromExample({customer: 'ACME', notes: null});
        var secondSample = zato.mapper.schema.inferFromExample({customer: 'Initech', notes: 'Deliver early', po_number: 'PO-1'});
        var merged = zato.mapper.schema.mergeNodes(firstSample, secondSample);

        check('a field present in both samples stays required', fieldByName(merged, 'customer').optional === false);
        checkEqual('a second sample refines an unknown leaf', fieldByName(merged, 'notes').node.types[0], 'string');
        check('a field present in only one sample becomes optional', fieldByName(merged, 'po_number').optional === true);
    }

// ////////////////////////////////////////////////////////////////////////
// JSON Schema import
// ////////////////////////////////////////////////////////////////////////

    function runJSONSchemaAssertions() {

        var document = {
            type: 'object',
            required: ['customer', 'total'],
            properties: {
                customer: {type: 'string', description: 'Customer name'},
                total: {type: 'number'},
                status: {type: 'string', enum: ['new', 'paid', 'shipped']},
                count: {type: 'integer'},
                pattern_field: {type: 'string', pattern: '^[A-Z]+$'},
                lines: {
                    type: 'array',
                    items: {$ref: '#/$defs/line'}
                }
            },
            $defs: {
                line: {
                    type: 'object',
                    required: ['sku'],
                    properties: {
                        sku: {type: 'string'}
                    }
                }
            }
        };

        var converted = zato.mapper.schema.fromJSONSchema(document);
        var root = converted.root;

        checkEqual('a JSON Schema object converts to an object node', root.kind, 'object');
        check('a required property is not optional', fieldByName(root, 'customer').optional === false);
        check('a property outside required is optional', fieldByName(root, 'status').optional === true);
        checkEqual('a description is kept on the node', fieldByName(root, 'customer').node.description, 'Customer name');
        checkEqual('an enum is kept on the node', fieldByName(root, 'status').node.enum.join(','), 'new,paid,shipped');
        checkEqual('integer folds into number', fieldByName(root, 'count').node.types[0], 'number');

        // A local reference resolves within the pasted document.
        var lines = fieldByName(root, 'lines').node;
        checkEqual('items with a local $ref resolve', lines.element.kind, 'object');
        checkEqual('the resolved element has its fields', lines.element.fields[0].name, 'sku');

        // A keyword outside the subset is reported, never silently dropped.
        check('an unsupported keyword is reported', converted.unsupported.length > 0);
        checkEqual('the unsupported keyword is named', converted.unsupported[0].keyword, 'pattern');
    }

// ////////////////////////////////////////////////////////////////////////
// Scaffolding
// ////////////////////////////////////////////////////////////////////////

    function runScaffoldAssertions() {

        var example = {
            customer: 'ACME',
            total: 125.5,
            is_priority: true,
            created: '2026-05-01',
            lines: [{sku: 'AA-11'}]
        };

        var root = zato.mapper.schema.inferFromExample(example);
        var scaffold = zato.mapper.schema.scaffold(root);

        checkEqual('a string scaffolds as the placeholder', scaffold.customer, zato.mapper.config.scaffoldValues.string);
        checkEqual('a number scaffolds as the placeholder', scaffold.total, zato.mapper.config.scaffoldValues.number);
        checkEqual('a boolean scaffolds as the placeholder', scaffold.is_priority, zato.mapper.config.scaffoldValues.boolean);
        checkEqual('a date hint scaffolds as a date placeholder', scaffold.created, zato.mapper.config.scaffoldFormatValues.date);
        checkEqual('an array scaffolds with one element', scaffold.lines.length, 1);
        checkEqual('the scaffolded element has its fields', scaffold.lines[0].sku, zato.mapper.config.scaffoldValues.string);

        // An enum scaffolds as its first allowed value.
        var enumLeaf = zato.mapper.schema.newLeafNode(['string'], '');
        enumLeaf.enum = ['new', 'paid'];
        checkEqual('an enum scaffolds as its first value', zato.mapper.schema.scaffold(enumLeaf), 'new');
    }

// ////////////////////////////////////////////////////////////////////////
// Named schemas
// ////////////////////////////////////////////////////////////////////////

    function runNamedSchemaAssertions() {

        // Start clean so earlier runs do not interfere.
        window.store.remove(zato.mapper.config.namedSchemasStorageKey);

        var root = zato.mapper.schema.inferFromExample({customer: 'ACME'});
        zato.mapper.schema.named.save('order', root);

        checkEqual('a saved schema appears in the list', zato.mapper.schema.named.list().join(','), 'order');
        checkEqual('a saved schema loads back', zato.mapper.schema.named.get('order').fields[0].name, 'customer');

        zato.mapper.schema.named.remove('order');
        checkEqual('a removed schema disappears from the list', zato.mapper.schema.named.list().length, 0);
    }

// ////////////////////////////////////////////////////////////////////////
// Path listing
// ////////////////////////////////////////////////////////////////////////

    function runPathListingAssertions() {

        var example = {
            customer: 'ACME',
            address: {city: 'Prague'},
            lines: [{sku: 'AA-11', quantity: 2}]
        };

        var root = zato.mapper.schema.inferFromExample(example);
        var paths = zato.mapper.schema.listPaths(root);

        checkEqual('every path is listed in tree order', paths.join(','), 'customer,address,address.city,lines,lines.sku,lines.quantity');
        checkEqual('an empty tree lists no paths', zato.mapper.schema.listPaths(null).length, 0);
    }

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

    function finish() {
        summary.textContent = passedCount + ' passed, ' + failedCount + ' failed';
        summary.setAttribute('data-complete', 'true');
        summary.setAttribute('data-passed', passedCount);
        summary.setAttribute('data-failed', failedCount);
    }

    runArtifactAssertions();
    runValidationAssertions();
    runStoreInstanceAssertions();
    runInferenceAssertions();
    runJSONSchemaAssertions();
    runScaffoldAssertions();
    runNamedSchemaAssertions();
    runPathListingAssertions();
    runBuilderAssertions();

    // The evaluator suite is asynchronous - the summary waits for it.
    var evaluatorRun = runEvaluatorAssertions();
    evaluatorRun.then(finish);

})(jQuery);
