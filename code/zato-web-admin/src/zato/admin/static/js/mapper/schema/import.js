
// Mapper kit - the JSON Schema importer and sample scaffolding.
// The supported JSON Schema subset is type, properties, items,
// required, enum and description, with $ref resolved within the pasted
// document only. Every keyword outside the subset is reported, never
// silently dropped. Scaffolding generates a sample payload from a
// schema tree with typed placeholder values.

(function($) {

    var config = zato.mapper.config;

// ////////////////////////////////////////////////////////////////////////

    var supportedKeywords = {
        type: true,
        properties: true,
        items: true,
        required: true,
        enum: true,
        description: true,
        $ref: true,
        $defs: true,
        definitions: true,
        $schema: true,
        $id: true,
        title: true
    };

    function resolveReference(reference, documentRoot) {

        // Only local references of the #/path/to/node form are supported.
        var parts = reference.replace('#/', '').split('/');
        var current = documentRoot;

        for (var partIdx = 0; partIdx < parts.length; partIdx++) {
            current = current[parts[partIdx]];
        }

        return current;
    }

// ////////////////////////////////////////////////////////////////////////

    function convertJSONSchemaNode(schemaNode, documentRoot, path, unsupported) {

        // Resolve a local reference first, then convert its target.
        if (schemaNode.$ref) {
            var resolved = resolveReference(schemaNode.$ref, documentRoot);
            var out = convertJSONSchemaNode(resolved, documentRoot, path, unsupported);
            return out;
        }

        // Record every keyword outside the supported subset.
        for (var keyword in schemaNode) {
            if (!supportedKeywords[keyword]) {
                unsupported.push({keyword: keyword, path: path});
            }
        }

        var description = '';
        if (typeof schemaNode.description === 'string') {
            description = schemaNode.description;
        }

        if (schemaNode.type === 'object') {
            var objectNode = zato.mapper.schema.newObjectNode();
            objectNode.description = description;

            var requiredNames = {};
            if (Array.isArray(schemaNode.required)) {
                for (var requiredIdx = 0; requiredIdx < schemaNode.required.length; requiredIdx++) {
                    requiredNames[schemaNode.required[requiredIdx]] = true;
                }
            }

            if (schemaNode.properties) {
                for (var name in schemaNode.properties) {
                    var childPath = path + '.properties.' + name;
                    var childNode = convertJSONSchemaNode(schemaNode.properties[name], documentRoot, childPath, unsupported);
                    var optional = !requiredNames[name];
                    objectNode.fields.push({name: name, optional: optional, node: childNode});
                }
            }

            return objectNode;
        }

        if (schemaNode.type === 'array') {
            var element;
            if (schemaNode.items) {
                element = convertJSONSchemaNode(schemaNode.items, documentRoot, path + '.items', unsupported);
            }
            else {
                element = zato.mapper.schema.newLeafNode(['unknown'], '');
            }

            var arrayNode = zato.mapper.schema.newArrayNode(element);
            arrayNode.description = description;
            return arrayNode;
        }

        // Scalar types - integer folds into number, a type list becomes a union.
        var types = [];
        if (typeof schemaNode.type === 'string') {
            types.push(schemaNode.type === 'integer' ? 'number' : schemaNode.type);
        }
        else if (Array.isArray(schemaNode.type)) {
            for (var typeIdx = 0; typeIdx < schemaNode.type.length; typeIdx++) {
                var typeName = schemaNode.type[typeIdx];
                if (typeName === 'integer') {
                    typeName = 'number';
                }
                if (types.indexOf(typeName) === -1) {
                    types.push(typeName);
                }
            }
        }
        else {
            types.push('unknown');
        }

        var leaf = zato.mapper.schema.newLeafNode(types, '');
        leaf.description = description;

        if (Array.isArray(schemaNode.enum)) {
            leaf.enum = schemaNode.enum.slice();
        }

        return leaf;
    }

// ////////////////////////////////////////////////////////////////////////

    // Converts a pasted JSON Schema document into a schema tree.
    // Returns {root, unsupported} where unsupported lists every keyword
    // outside the supported subset together with where it was found.
    zato.mapper.schema.fromJSONSchema = function(document) {

        var unsupported = [];
        var root = convertJSONSchemaNode(document, document, '$', unsupported);

        var out = {root: root, unsupported: unsupported};
        return out;
    };

// ////////////////////////////////////////////////////////////////////////
// Sample scaffolding - generates a sample payload from a schema tree
// with typed placeholder values. A new scaffold is always a new sample,
// it never overwrites anything the user typed.
// ////////////////////////////////////////////////////////////////////////

    function scaffoldNode(node) {

        if (node.kind === 'object') {
            var out = {};
            for (var fieldIdx = 0; fieldIdx < node.fields.length; fieldIdx++) {
                var field = node.fields[fieldIdx];
                out[field.name] = scaffoldNode(field.node);
            }
            return out;
        }

        if (node.kind === 'array') {
            var element = scaffoldNode(node.element);
            var arrayOut = [element];
            return arrayOut;
        }

        // An enum picks its first allowed value ..
        if (node.enum.length > 0) {
            var enumOut = node.enum[0];
            return enumOut;
        }

        // .. a format hint picks its placeholder ..
        if (node.format !== '') {
            var formatOut = config.scaffoldFormatValues[node.format];
            return formatOut;
        }

        // .. a union scaffolds as its first type, unknown as null.
        var leafOut = config.scaffoldValues[node.types[0]];
        return leafOut;
    }

    zato.mapper.schema.scaffold = scaffoldNode;

})(jQuery);
