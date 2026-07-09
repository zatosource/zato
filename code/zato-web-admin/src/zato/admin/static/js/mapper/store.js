
// Mapper kit - the artifact store.
// The mapping artifact is one JSON document with a stable key order.
// Everything the UI shows is a projection of this store and every
// change goes through one of its mutations, which validate the model,
// keep undo and redo snapshots and autosave to browser storage.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.store = {};

// ////////////////////////////////////////////////////////////////////////

    // Returns a new mapping row in the canonical shape. A null default
    // means no default, omit_if_empty controls whether an empty result
    // omits the target field instead of writing it.
    zato.mapper.store.newMapping = function() {
        return {
            target: '',
            expression: '',
            condition: '',
            comment: '',
            origin: '',
            'default': null,
            omit_if_empty: false
        };
    };

// ////////////////////////////////////////////////////////////////////////

    // Returns a new, empty artifact in the canonical shape.
    zato.mapper.store.newArtifact = function() {
        return {
            version: config.artifactVersion,
            name: config.defaultName,
            description: config.defaultDescription,
            source_schema: {read_only: false, root: null},
            target_schema: {read_only: false, root: null},
            mappings: [],
            scopes: [],
            functions: [],
            lookup_tables: [],
            tests: [],
            samples: []
        };
    };

// ////////////////////////////////////////////////////////////////////////
// Deterministic serialization - each serializer builds a fresh object
// whose keys are inserted in one fixed order, so the same model always
// produces byte-identical JSON.
// ////////////////////////////////////////////////////////////////////////

    function serializeNode(node) {
        if (node === null) {
            return null;
        }

        var out = {kind: node.kind, description: node.description};

        if (node.kind === 'object') {
            out.fields = [];
            for (var fieldIdx = 0; fieldIdx < node.fields.length; fieldIdx++) {
                var field = node.fields[fieldIdx];
                out.fields.push({
                    name: field.name,
                    optional: field.optional,
                    node: serializeNode(field.node)
                });
            }
        }
        else if (node.kind === 'array') {
            out.element = serializeNode(node.element);
        }
        else {
            out.types = node.types.slice();
            out.format = node.format;
            out.enum = node.enum.slice();
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function serializeSchema(schema) {
        return {
            read_only: schema.read_only,
            root: serializeNode(schema.root)
        };
    }

// ////////////////////////////////////////////////////////////////////////

    function serializeMapping(row) {
        return {
            target: row.target,
            expression: row.expression,
            condition: row.condition,
            comment: row.comment,
            origin: row.origin,
            'default': row['default'],
            omit_if_empty: row.omit_if_empty
        };
    }

// ////////////////////////////////////////////////////////////////////////

    function serializeScope(scope) {

        // Child rows are serialized with the same row serializer
        // so nested and top-level rows always share one shape.
        var childRows = [];
        for (var rowIdx = 0; rowIdx < scope.mappings.length; rowIdx++) {
            childRows.push(serializeMapping(scope.mappings[rowIdx]));
        }

        return {
            target: scope.target,
            source: scope.source,
            mappings: childRows
        };
    }

// ////////////////////////////////////////////////////////////////////////

    function serializeFunction(item) {
        return {
            name: item.name,
            parameters: item.parameters.slice(),
            body: item.body,
            description: item.description
        };
    }

// ////////////////////////////////////////////////////////////////////////

    function serializeLookupTable(item) {
        var rows = [];
        for (var rowIdx = 0; rowIdx < item.rows.length; rowIdx++) {
            rows.push(item.rows[rowIdx].slice());
        }

        return {
            name: item.name,
            columns: item.columns.slice(),
            rows: rows
        };
    }

// ////////////////////////////////////////////////////////////////////////

    function serializeTest(item) {
        return {
            name: item.name,
            input: item.input,
            expected: item.expected
        };
    }

// ////////////////////////////////////////////////////////////////////////

    function serializeSample(item) {
        return {
            name: item.name,
            side: item.side,
            payload: item.payload
        };
    }

// ////////////////////////////////////////////////////////////////////////

    // Serializes the whole artifact into pretty-printed JSON text
    // with a stable key order at every level.
    zato.mapper.store.serialize = function(artifact) {

        var mappings = [];
        for (var mappingIdx = 0; mappingIdx < artifact.mappings.length; mappingIdx++) {
            mappings.push(serializeMapping(artifact.mappings[mappingIdx]));
        }

        var scopes = [];
        for (var scopeIdx = 0; scopeIdx < artifact.scopes.length; scopeIdx++) {
            scopes.push(serializeScope(artifact.scopes[scopeIdx]));
        }

        var functions = [];
        for (var functionIdx = 0; functionIdx < artifact.functions.length; functionIdx++) {
            functions.push(serializeFunction(artifact.functions[functionIdx]));
        }

        var lookupTables = [];
        for (var tableIdx = 0; tableIdx < artifact.lookup_tables.length; tableIdx++) {
            lookupTables.push(serializeLookupTable(artifact.lookup_tables[tableIdx]));
        }

        var tests = [];
        for (var testIdx = 0; testIdx < artifact.tests.length; testIdx++) {
            tests.push(serializeTest(artifact.tests[testIdx]));
        }

        var samples = [];
        for (var sampleIdx = 0; sampleIdx < artifact.samples.length; sampleIdx++) {
            samples.push(serializeSample(artifact.samples[sampleIdx]));
        }

        var ordered = {
            version: artifact.version,
            name: artifact.name,
            description: artifact.description,
            source_schema: serializeSchema(artifact.source_schema),
            target_schema: serializeSchema(artifact.target_schema),
            mappings: mappings,
            scopes: scopes,
            functions: functions,
            lookup_tables: lookupTables,
            tests: tests,
            samples: samples
        };

        var out = JSON.stringify(ordered, null, config.jsonIndent);
        return out;
    };

// ////////////////////////////////////////////////////////////////////////
// Validation - returns a list of {code, path, message} records.
// An empty list means the artifact is structurally sound and every
// expression in it parses.
// ////////////////////////////////////////////////////////////////////////

    var leafTypes = {string: true, number: true, boolean: true, object: true, array: true, unknown: true};

    function validateNode(node, path, records) {
        if (node === null) {
            return;
        }

        if (node.kind === 'object') {
            if (!Array.isArray(node.fields)) {
                records.push({code: 'schema-fields-not-list', path: path, message: 'Object node has no field list'});
                return;
            }

            var seenNames = {};
            for (var fieldIdx = 0; fieldIdx < node.fields.length; fieldIdx++) {
                var field = node.fields[fieldIdx];
                var fieldPath = path + '.fields[' + fieldIdx + ']';

                if (typeof field.name !== 'string' || field.name === '') {
                    records.push({code: 'schema-field-name', path: fieldPath, message: 'Field name must be a non-empty string'});
                    continue;
                }
                if (seenNames[field.name]) {
                    records.push({code: 'schema-field-duplicate', path: fieldPath, message: 'Duplicate field name `' + field.name + '`'});
                }
                seenNames[field.name] = true;

                if (typeof field.optional !== 'boolean') {
                    records.push({code: 'schema-field-optional', path: fieldPath, message: 'Field `' + field.name + '` has no boolean optional flag'});
                }

                validateNode(field.node, fieldPath + '.node', records);
            }
        }
        else if (node.kind === 'array') {
            validateNode(node.element, path + '.element', records);
        }
        else if (node.kind === 'leaf') {
            if (!Array.isArray(node.types) || node.types.length === 0) {
                records.push({code: 'schema-leaf-types', path: path, message: 'Leaf node has no type list'});
                return;
            }
            for (var typeIdx = 0; typeIdx < node.types.length; typeIdx++) {
                if (!leafTypes[node.types[typeIdx]]) {
                    records.push({code: 'schema-leaf-type-unknown', path: path, message: 'Unknown leaf type `' + node.types[typeIdx] + '`'});
                }
            }
        }
        else {
            records.push({code: 'schema-kind-unknown', path: path, message: 'Unknown node kind `' + node.kind + '`'});
        }
    }

// ////////////////////////////////////////////////////////////////////////

    function validateExpression(text, path, code, records) {
        try {
            jsonata(text);
        } catch(error) {
            records.push({code: code, path: path, message: error.message});
        }
    }

// ////////////////////////////////////////////////////////////////////////

    function validateMapping(row, path, records) {
        if (typeof row.target !== 'string' || row.target === '') {
            records.push({code: 'mapping-target', path: path, message: 'Mapping target must be a non-empty string'});
        }
        if (typeof row.expression !== 'string' || row.expression === '') {
            records.push({code: 'mapping-expression', path: path, message: 'Mapping expression must be a non-empty string'});
        }
        else {
            validateExpression(row.expression, path + '.expression', 'mapping-expression-parse', records);
        }

        // A condition is optional but must parse when present.
        if (row.condition !== '') {
            validateExpression(row.condition, path + '.condition', 'mapping-condition-parse', records);
        }

        if (typeof row.omit_if_empty !== 'boolean') {
            records.push({code: 'mapping-omit-flag', path: path, message: 'Mapping omit_if_empty must be a boolean'});
        }
    }

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.store.validate = function(artifact) {

        var records = [];

        if (artifact.version !== config.artifactVersion) {
            records.push({code: 'artifact-version', path: 'version', message: 'Unsupported artifact version `' + artifact.version + '`'});
        }
        if (typeof artifact.name !== 'string' || artifact.name === '') {
            records.push({code: 'artifact-name', path: 'name', message: 'Artifact name must be a non-empty string'});
        }

        // The artifact may come from an uploaded file, so every list-valued
        // key is checked before anything iterates over it - a missing list
        // ends validation here because nothing below could run.
        var listKeys = ['mappings', 'scopes', 'functions', 'lookup_tables', 'tests', 'samples'];
        var hasListErrors = false;

        for (var listIdx = 0; listIdx < listKeys.length; listIdx++) {
            if (!Array.isArray(artifact[listKeys[listIdx]])) {
                records.push({code: 'artifact-list', path: listKeys[listIdx], message: '`' + listKeys[listIdx] + '` must be a list'});
                hasListErrors = true;
            }
        }
        if (hasListErrors) {
            return records;
        }

        // Both schemas must exist and their trees must be sound ..
        var sideKeys = ['source_schema', 'target_schema'];
        for (var sideIdx = 0; sideIdx < sideKeys.length; sideIdx++) {
            var sideKey = sideKeys[sideIdx];
            var schema = artifact[sideKey];

            if (!schema || typeof schema.read_only !== 'boolean') {
                records.push({code: 'schema-shape', path: sideKey, message: 'Schema must have a boolean read_only flag'});
                continue;
            }
            validateNode(schema.root, sideKey + '.root', records);
        }

        // .. every top-level mapping row must be sound ..
        for (var mappingIdx = 0; mappingIdx < artifact.mappings.length; mappingIdx++) {
            validateMapping(artifact.mappings[mappingIdx], 'mappings[' + mappingIdx + ']', records);
        }

        // .. every scope must have a parseable source selector and sound child rows ..
        for (var scopeIdx = 0; scopeIdx < artifact.scopes.length; scopeIdx++) {
            var scope = artifact.scopes[scopeIdx];
            var scopePath = 'scopes[' + scopeIdx + ']';

            if (typeof scope.target !== 'string' || scope.target === '') {
                records.push({code: 'scope-target', path: scopePath, message: 'Scope target must be a non-empty string'});
            }
            if (typeof scope.source !== 'string' || scope.source === '') {
                records.push({code: 'scope-source', path: scopePath, message: 'Scope source must be a non-empty string'});
            }
            else {
                validateExpression(scope.source, scopePath + '.source', 'scope-source-parse', records);
            }

            // Child rows of an uploaded scope may be missing outright.
            if (!Array.isArray(scope.mappings)) {
                records.push({code: 'scope-mappings', path: scopePath, message: 'Scope mappings must be a list'});
                continue;
            }

            for (var childIdx = 0; childIdx < scope.mappings.length; childIdx++) {
                validateMapping(scope.mappings[childIdx], scopePath + '.mappings[' + childIdx + ']', records);
            }
        }

        // .. every user-defined function body must parse ..
        for (var functionIdx = 0; functionIdx < artifact.functions.length; functionIdx++) {
            var item = artifact.functions[functionIdx];
            var functionPath = 'functions[' + functionIdx + ']';

            if (typeof item.name !== 'string' || item.name === '') {
                records.push({code: 'function-name', path: functionPath, message: 'Function name must be a non-empty string'});
            }
            validateExpression(item.body, functionPath + '.body', 'function-body-parse', records);
        }

        // .. every sample must have a name and a known side ..
        for (var sampleIdx = 0; sampleIdx < artifact.samples.length; sampleIdx++) {
            var sample = artifact.samples[sampleIdx];
            var samplePath = 'samples[' + sampleIdx + ']';

            if (typeof sample.name !== 'string' || sample.name === '') {
                records.push({code: 'sample-name', path: samplePath, message: 'Sample name must be a non-empty string'});
            }
            if (config.sides.indexOf(sample.side) === -1) {
                records.push({code: 'sample-side', path: samplePath, message: 'Sample side must be one of: ' + config.sides.join(', ')});
            }
        }

        // .. and every test case must have a name.
        for (var testIdx = 0; testIdx < artifact.tests.length; testIdx++) {
            var testCase = artifact.tests[testIdx];
            if (typeof testCase.name !== 'string' || testCase.name === '') {
                records.push({code: 'test-name', path: 'tests[' + testIdx + ']', message: 'Test name must be a non-empty string'});
            }
        }

        return records;
    };

// ////////////////////////////////////////////////////////////////////////
// The store instance - holds one artifact, applies validated mutations,
// keeps undo and redo snapshots and autosaves after every change.
// ////////////////////////////////////////////////////////////////////////

    zato.mapper.store.create = function(createConfig) {

        var artifact;
        var undoStack = [];
        var redoStack = [];
        var listeners = [];
        var storageKey = createConfig.storageKey;

        // Restore the autosaved artifact if browser storage has a valid one,
        // otherwise start from an empty artifact. Storage content is an
        // external boundary, so it is parsed and validated explicitly.
        var saved = window.store.get(storageKey);
        if (saved) {
            var parsed = null;
            try {
                parsed = JSON.parse(saved);
            } catch(error) {
                parsed = null;
                zato.mapper.log('store', 'the autosaved artifact is not valid JSON', {storageKey: storageKey, error: error.message});
            }
            if (parsed) {
                var savedRecords = zato.mapper.store.validate(parsed);
                if (savedRecords.length === 0) {
                    artifact = parsed;
                }
                else {
                    zato.mapper.log('store', 'the autosaved artifact failed validation and is discarded', {storageKey: storageKey, records: savedRecords});
                }
            }
        }
        if (artifact) {
            zato.mapper.log('store', 'restored the autosaved artifact', {storageKey: storageKey, name: artifact.name, mappings: artifact.mappings.length, scopes: artifact.scopes.length, samples: artifact.samples.length});
        }
        else {
            artifact = zato.mapper.store.newArtifact();
            zato.mapper.log('store', 'started with a new, empty artifact', {storageKey: storageKey});
        }

        function notify() {
            for (var listenerIdx = 0; listenerIdx < listeners.length; listenerIdx++) {
                listeners[listenerIdx](artifact);
            }
        }

        function snapshot() {
            var out = zato.mapper.store.serialize(artifact);
            return out;
        }

        function autosave() {
            window.store.set(storageKey, snapshot());
        }

        // Every mutation runs through here: the previous state goes onto
        // the undo stack, the redo stack is cleared, the change is applied,
        // then the artifact is autosaved, logged and all listeners re-render.
        function mutate(label, data, applyChange) {
            undoStack.push(snapshot());
            if (undoStack.length > config.undoLimit) {
                undoStack.shift();
            }
            redoStack = [];

            applyChange(artifact);

            autosave();

            zato.mapper.log('store', 'mutation ' + label, data);

            var records = zato.mapper.store.validate(artifact);
            if (records.length > 0) {
                zato.mapper.log('store', 'the artifact has validation records after ' + label, records);
            }

            notify();
        }

        var instance = {

            getArtifact: function() {
                return artifact;
            },

            serialize: function() {
                var out = snapshot();
                return out;
            },

            validate: function() {
                var out = zato.mapper.store.validate(artifact);
                return out;
            },

            subscribe: function(listener) {
                listeners.push(listener);
            },

            // Replaces the whole artifact, e.g. from an imported file.
            // Returns the validation records - the artifact is replaced
            // only when the list is empty.
            loadArtifact: function(candidate) {
                var records = zato.mapper.store.validate(candidate);
                if (records.length === 0) {
                    mutate('loadArtifact', {name: candidate.name}, function() {
                        artifact = candidate;
                    });
                }
                else {
                    zato.mapper.log('store', 'loadArtifact rejected the candidate', records);
                }

                return records;
            },

            setName: function(name) {
                mutate('setName', {name: name}, function(current) {
                    current.name = name;
                });
            },

            setDescription: function(description) {
                mutate('setDescription', {description: description}, function(current) {
                    current.description = description;
                });
            },

            // Replaces one side's schema tree. The side is 'source' or 'target'.
            setSchemaRoot: function(side, root) {
                mutate('setSchemaRoot', {side: side}, function(current) {
                    current[side + '_schema'].root = root;
                });
            },

            addSample: function(sample) {
                mutate('addSample', {name: sample.name, side: sample.side}, function(current) {
                    current.samples.push(sample);
                });
            },

            addMapping: function(row) {
                mutate('addMapping', row, function(current) {
                    current.mappings.push(row);
                });
            },

            updateMapping: function(rowIndex, row) {
                mutate('updateMapping', {rowIndex: rowIndex, row: row}, function(current) {
                    current.mappings[rowIndex] = row;
                });
            },

            removeMapping: function(rowIndex) {
                mutate('removeMapping', {rowIndex: rowIndex}, function(current) {
                    current.mappings.splice(rowIndex, 1);
                });
            },

            addScope: function(scope) {
                mutate('addScope', {target: scope.target, source: scope.source, rows: scope.mappings.length}, function(current) {
                    current.scopes.push(scope);
                });
            },

            addScopeMapping: function(scopeIndex, row) {
                mutate('addScopeMapping', {scopeIndex: scopeIndex, row: row}, function(current) {
                    current.scopes[scopeIndex].mappings.push(row);
                });
            },

            updateScopeMapping: function(scopeIndex, rowIndex, row) {
                mutate('updateScopeMapping', {scopeIndex: scopeIndex, rowIndex: rowIndex, row: row}, function(current) {
                    current.scopes[scopeIndex].mappings[rowIndex] = row;
                });
            },

            removeScopeMapping: function(scopeIndex, rowIndex) {
                mutate('removeScopeMapping', {scopeIndex: scopeIndex, rowIndex: rowIndex}, function(current) {
                    current.scopes[scopeIndex].mappings.splice(rowIndex, 1);
                });
            },

            // Applies accepted auto-map suggestions in one undoable step:
            // new top-level rows, new scopes with their children, and
            // child rows added into scopes that already exist.
            applyAutoMap: function(rows, scopes, scopeAdditions) {
                mutate('applyAutoMap', {rows: rows.length, scopes: scopes.length, additions: scopeAdditions.length}, function(current) {

                    for (var rowIdx = 0; rowIdx < rows.length; rowIdx++) {
                        current.mappings.push(rows[rowIdx]);
                    }

                    for (var scopeIdx = 0; scopeIdx < scopes.length; scopeIdx++) {
                        current.scopes.push(scopes[scopeIdx]);
                    }

                    for (var additionIdx = 0; additionIdx < scopeAdditions.length; additionIdx++) {
                        var addition = scopeAdditions[additionIdx];
                        for (var childIdx = 0; childIdx < addition.rows.length; childIdx++) {
                            current.scopes[addition.scopeIndex].mappings.push(addition.rows[childIdx]);
                        }
                    }
                });
            },

            // Replaces one side's schema tree together with the whole
            // mapping and scope lists in one undoable step - the shape
            // a field rename or a schema re-import produces. The sample
            // is null when the edit brings no new sample along.
            applySchemaEdit: function(side, root, mappings, scopes, sample) {
                mutate('applySchemaEdit', {side: side, mappings: mappings.length, scopes: scopes.length}, function(current) {
                    current[side + '_schema'].root = root;
                    current.mappings = mappings;
                    current.scopes = scopes;

                    if (sample !== null) {
                        current.samples.push(sample);
                    }
                });
            },

            // Removes every mapping row and scope in one undoable step.
            clearMappings: function() {
                mutate('clearMappings', {}, function(current) {
                    current.mappings = [];
                    current.scopes = [];
                });
            },

            canUndo: function() {
                var out = undoStack.length > 0;
                return out;
            },

            canRedo: function() {
                var out = redoStack.length > 0;
                return out;
            },

            undo: function() {
                if (undoStack.length === 0) {
                    return;
                }

                // The current state becomes redoable, the previous one current.
                redoStack.push(snapshot());
                artifact = JSON.parse(undoStack.pop());

                autosave();
                zato.mapper.log('store', 'undo', {undoLeft: undoStack.length, redoLeft: redoStack.length});
                notify();
            },

            redo: function() {
                if (redoStack.length === 0) {
                    return;
                }

                // The current state becomes undoable again, the redone one current.
                undoStack.push(snapshot());
                artifact = JSON.parse(redoStack.pop());

                autosave();
                zato.mapper.log('store', 'redo', {undoLeft: undoStack.length, redoLeft: redoStack.length});
                notify();
            }
        };

        return instance;
    };

})(jQuery);
