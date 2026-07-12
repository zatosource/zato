
// Mapper kit - the artifact shape and its serialization.
// The mapping artifact is one JSON document with a stable key order.
// Each serializer builds a fresh object whose keys are inserted in one
// fixed order, so the same model always produces byte-identical JSON.
// The validation and the store instance live in the other store/ files.

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

})(jQuery);
