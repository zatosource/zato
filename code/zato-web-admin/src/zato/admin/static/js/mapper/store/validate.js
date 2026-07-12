
// Mapper kit - artifact validation.
// Returns a list of {code, path, message} records. An empty list means
// the artifact is structurally sound and every expression in it parses.

(function($) {

    var config = zato.mapper.config;

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

})(jQuery);
