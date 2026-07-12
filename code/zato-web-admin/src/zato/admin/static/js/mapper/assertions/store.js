
// Mapper - browser assertions for the store.
// The artifact shape, deterministic serialization, validation and the
// store instance with its mutations, undo and redo and autosave.

(function($) {

    var check = zato.mapper.assertions.check;
    var checkEqual = zato.mapper.assertions.checkEqual;
    var findRecord = zato.mapper.assertions.findRecord;
    var makeRow = zato.mapper.assertions.makeRow;
    var assertionStorageKey = zato.mapper.assertions.storageKey;

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

    runArtifactAssertions();
    runValidationAssertions();
    runStoreInstanceAssertions();

})(jQuery);
