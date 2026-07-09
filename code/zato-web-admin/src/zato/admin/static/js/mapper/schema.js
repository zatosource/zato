
// Mapper kit - schemas.
// Inference from a pasted JSON example, merging of multiple samples,
// a JSON Schema subset importer, sample scaffolding and named schemas
// kept in browser storage.

(function($) {

    var config = zato.mapper.config;

    zato.mapper.schema = {};

// ////////////////////////////////////////////////////////////////////////
// Node constructors - every node carries the same fixed set of keys
// for its kind so serialization stays deterministic.
// ////////////////////////////////////////////////////////////////////////

    function newObjectNode() {
        return {kind: 'object', description: '', fields: []};
    }

    function newArrayNode(element) {
        return {kind: 'array', description: '', element: element};
    }

    function newLeafNode(types, format) {
        return {kind: 'leaf', description: '', types: types, format: format, enum: []};
    }

    zato.mapper.schema.newObjectNode = newObjectNode;
    zato.mapper.schema.newArrayNode = newArrayNode;
    zato.mapper.schema.newLeafNode = newLeafNode;

// ////////////////////////////////////////////////////////////////////////
// String format detection - a display hint only, it never causes coercion.
// ////////////////////////////////////////////////////////////////////////

    var datePattern = /^\d{4}-\d{2}-\d{2}$/;
    var datetimePattern = /^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$/;
    var timePattern = /^\d{2}:\d{2}(:\d{2})?(\.\d+)?$/;

    function detectFormat(value) {
        if (datePattern.test(value)) {
            return 'date';
        }
        if (datetimePattern.test(value)) {
            return 'datetime';
        }
        if (timePattern.test(value)) {
            return 'time';
        }

        return '';
    }

    zato.mapper.schema.detectFormat = detectFormat;

// ////////////////////////////////////////////////////////////////////////
// Inference from an example - walk the example recursively, preserving
// field order exactly as pasted. Nulls become leaves of unknown type,
// arrays merge the schemas of all their elements.
// ////////////////////////////////////////////////////////////////////////

    function typeNameOf(node) {
        if (node.kind === 'object') {
            return 'object';
        }
        if (node.kind === 'array') {
            return 'array';
        }

        var out = node.types[0];
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Merges the type lists of two leaf nodes: unknown always gives way
    // to a real type, disagreeing real types become a recorded union.
    function mergeTypeLists(first, second) {

        var out = [];

        for (var firstIdx = 0; firstIdx < first.length; firstIdx++) {
            if (first[firstIdx] !== 'unknown') {
                out.push(first[firstIdx]);
            }
        }
        for (var secondIdx = 0; secondIdx < second.length; secondIdx++) {
            if (second[secondIdx] !== 'unknown') {
                if (out.indexOf(second[secondIdx]) === -1) {
                    out.push(second[secondIdx]);
                }
            }
        }

        // Both sides were unknown, so the merge stays unknown.
        if (out.length === 0) {
            out.push('unknown');
        }

        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    // Merges two nodes per the sample-merging rules: objects union their
    // fields (a field absent from one side becomes optional), arrays merge
    // their elements, leaves union their types, and a structural mismatch
    // is recorded as a union of the two shapes - never a silent pick of one.
    function mergeNodes(first, second) {

        // Unknown leaves are refined by whatever the other side knows.
        if (first.kind === 'leaf') {
            if (first.types.length === 1) {
                if (first.types[0] === 'unknown') {
                    return second;
                }
            }
        }
        if (second.kind === 'leaf') {
            if (second.types.length === 1) {
                if (second.types[0] === 'unknown') {
                    return first;
                }
            }
        }

        if (first.kind === 'object') {
            if (second.kind === 'object') {

                var out = newObjectNode();
                var secondByName = {};
                var secondSeen = {};

                for (var secondIdx = 0; secondIdx < second.fields.length; secondIdx++) {
                    secondByName[second.fields[secondIdx].name] = second.fields[secondIdx];
                }

                // Fields of the first side keep their order ..
                for (var firstIdx = 0; firstIdx < first.fields.length; firstIdx++) {
                    var firstField = first.fields[firstIdx];
                    var counterpart = secondByName[firstField.name];

                    if (counterpart) {
                        secondSeen[firstField.name] = true;
                        var mergedNode = mergeNodes(firstField.node, counterpart.node);
                        var mergedOptional = firstField.optional;
                        if (counterpart.optional) {
                            mergedOptional = true;
                        }
                        out.fields.push({name: firstField.name, optional: mergedOptional, node: mergedNode});
                    }
                    else {
                        // Present on one side only, so the field becomes optional.
                        out.fields.push({name: firstField.name, optional: true, node: firstField.node});
                    }
                }

                // .. and fields only the second side has follow, also optional.
                for (var extraIdx = 0; extraIdx < second.fields.length; extraIdx++) {
                    var extraField = second.fields[extraIdx];
                    if (!secondSeen[extraField.name]) {
                        out.fields.push({name: extraField.name, optional: true, node: extraField.node});
                    }
                }

                return out;
            }
        }

        if (first.kind === 'array') {
            if (second.kind === 'array') {
                var mergedElement = mergeNodes(first.element, second.element);
                var mergedArray = newArrayNode(mergedElement);
                return mergedArray;
            }
        }

        if (first.kind === 'leaf') {
            if (second.kind === 'leaf') {
                var mergedTypes = mergeTypeLists(first.types, second.types);

                // A format hint survives only when both sides agree on it.
                var mergedFormat = '';
                if (first.format === second.format) {
                    mergedFormat = first.format;
                }

                var mergedLeaf = newLeafNode(mergedTypes, mergedFormat);
                return mergedLeaf;
            }
        }

        // Structural mismatch - record a union of the two shapes.
        var mismatchTypes = mergeTypeLists([typeNameOf(first)], [typeNameOf(second)]);

        var out = newLeafNode(mismatchTypes, '');
        return out;
    }

    zato.mapper.schema.mergeNodes = mergeNodes;

// ////////////////////////////////////////////////////////////////////////

    function inferNode(value) {

        if (value === null) {
            var unknownLeaf = newLeafNode(['unknown'], '');
            return unknownLeaf;
        }

        if (Array.isArray(value)) {

            // An empty array has an unknown element type until
            // another sample refines it.
            if (value.length === 0) {
                var emptyElement = newLeafNode(['unknown'], '');
                var emptyArray = newArrayNode(emptyElement);
                return emptyArray;
            }

            // The element schema is the merge of all elements.
            var element = inferNode(value[0]);
            for (var elementIdx = 1; elementIdx < value.length; elementIdx++) {
                var nextElement = inferNode(value[elementIdx]);
                element = mergeNodes(element, nextElement);
            }

            var out = newArrayNode(element);
            return out;
        }

        if (typeof value === 'object') {
            var objectNode = newObjectNode();

            for (var name in value) {
                var fieldNode = inferNode(value[name]);
                objectNode.fields.push({name: name, optional: false, node: fieldNode});
            }

            return objectNode;
        }

        if (typeof value === 'string') {
            var format = detectFormat(value);
            var stringLeaf = newLeafNode(['string'], format);
            return stringLeaf;
        }

        if (typeof value === 'number') {
            var numberLeaf = newLeafNode(['number'], '');
            return numberLeaf;
        }

        // The only remaining JSON type is boolean.
        var booleanLeaf = newLeafNode(['boolean'], '');
        return booleanLeaf;
    }

    zato.mapper.schema.inferFromExample = inferNode;

// ////////////////////////////////////////////////////////////////////////
// JSON Schema import - the supported subset is type, properties, items,
// required, enum and description, with $ref resolved within the pasted
// document only. Every keyword outside the subset is reported, never
// silently dropped.
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
            var objectNode = newObjectNode();
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
                element = newLeafNode(['unknown'], '');
            }

            var arrayNode = newArrayNode(element);
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

        var leaf = newLeafNode(types, '');
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

// ////////////////////////////////////////////////////////////////////////
// Path listing - every dotted path a schema tree contains, used by
// autocomplete and by the expression builder's field pills.
// ////////////////////////////////////////////////////////////////////////

    function collectPaths(node, prefix, out) {

        var fields;
        if (node.kind === 'object') {
            fields = node.fields;
        }
        else if (node.kind === 'array') {
            if (node.element.kind === 'object') {
                fields = node.element.fields;
            }
            else {
                return;
            }
        }
        else {
            return;
        }

        for (var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
            var field = fields[fieldIdx];
            var path = prefix === '' ? field.name : prefix + '.' + field.name;

            out.push(path);
            collectPaths(field.node, path, out);
        }
    }

// ////////////////////////////////////////////////////////////////////////

    // Returns every dotted path in the tree, in tree order.
    zato.mapper.schema.listPaths = function(root) {

        var out = [];
        if (root !== null) {
            collectPaths(root, '', out);
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    function collectFields(node, prefix, out) {

        var fields;
        if (node.kind === 'object') {
            fields = node.fields;
        }
        else if (node.kind === 'array') {
            if (node.element.kind === 'object') {
                fields = node.element.fields;
            }
            else {
                return;
            }
        }
        else {
            return;
        }

        for (var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
            var field = fields[fieldIdx];
            var path = prefix === '' ? field.name : prefix + '.' + field.name;

            out.push({path: path, name: field.name, node: field.node, optional: field.optional});
            collectFields(field.node, path, out);
        }
    }

// ////////////////////////////////////////////////////////////////////////

    // Returns every field in the tree as {path, name, node, optional},
    // in tree order - the richer companion of listPaths for callers that
    // need the nodes themselves, like the filters and auto-map.
    zato.mapper.schema.listFields = function(root) {

        var out = [];
        if (root !== null) {
            collectFields(root, '', out);
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Returns a deep copy of a schema node.
    zato.mapper.schema.clone = function(node) {

        var out = JSON.parse(JSON.stringify(node));
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Renames the field a dotted path points at, returning {root, error} -
    // the root is a new tree with the rename applied, the input tree is
    // never touched. An unresolvable path or a sibling name clash is an
    // error and the original root comes back unchanged.
    zato.mapper.schema.renameField = function(root, path, newName) {

        var cloned = zato.mapper.schema.clone(root);
        var segments = path.split('.');

        // Walk down to the node holding the renamed field ..
        var holder = cloned;
        for (var segmentIdx = 0; segmentIdx < segments.length - 1; segmentIdx++) {
            holder = fieldNodeOf(holder, segments[segmentIdx]);
            if (holder === null) {
                return {root: root, error: 'No field exists at `' + path + '`'};
            }
        }

        // .. the fields looked into are the holder's own or its element's ..
        var fields;
        if (holder.kind === 'object') {
            fields = holder.fields;
        }
        else if (holder.kind === 'array' && holder.element.kind === 'object') {
            fields = holder.element.fields;
        }
        else {
            return {root: root, error: 'No field exists at `' + path + '`'};
        }

        // .. a sibling already using the new name is a clash ..
        var oldName = segments[segments.length - 1];
        var renamedField = null;

        for (var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
            if (fields[fieldIdx].name === newName) {
                return {root: root, error: 'A sibling field is already named `' + newName + '`'};
            }
            if (fields[fieldIdx].name === oldName) {
                renamedField = fields[fieldIdx];
            }
        }

        if (renamedField === null) {
            return {root: root, error: 'No field exists at `' + path + '`'};
        }

        // .. and the rename itself keeps the field's node and position.
        renamedField.name = newName;

        var out = {root: cloned, error: ''};
        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    function fieldNodeOf(node, name) {

        // The fields looked into: an object's own, an array's element's.
        var fields;
        if (node.kind === 'object') {
            fields = node.fields;
        }
        else if (node.kind === 'array' && node.element.kind === 'object') {
            fields = node.element.fields;
        }
        else {
            return null;
        }

        for (var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
            if (fields[fieldIdx].name === name) {
                var out = fields[fieldIdx].node;
                return out;
            }
        }

        return null;
    }

// ////////////////////////////////////////////////////////////////////////

    // Returns the node a dotted path points at, or null when the path
    // leads nowhere in this tree.
    zato.mapper.schema.nodeAtPath = function(root, path) {

        var segments = path.split('.');
        var current = root;

        for (var segmentIdx = 0; segmentIdx < segments.length; segmentIdx++) {
            current = fieldNodeOf(current, segments[segmentIdx]);
            if (current === null) {
                return null;
            }
        }

        return current;
    };

// ////////////////////////////////////////////////////////////////////////

    // Returns the path of the nearest strict ancestor of the path that
    // is a repeating node, or '' when the path sits outside any list.
    zato.mapper.schema.nearestArrayAncestor = function(root, path) {

        var segments = path.split('.');
        var current = root;
        var out = '';

        // Only strict ancestors count, so the last segment is skipped.
        for (var segmentIdx = 0; segmentIdx < segments.length - 1; segmentIdx++) {
            current = fieldNodeOf(current, segments[segmentIdx]);
            if (current === null) {
                return out;
            }
            if (current.kind === 'array') {
                out = segments.slice(0, segmentIdx + 1).join('.');
            }
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////
// Named schemas - stored once in browser storage, referenced by many
// mappings.
// ////////////////////////////////////////////////////////////////////////

    zato.mapper.schema.named = {};

    function readNamed() {

        // Browser storage is an external boundary, so absence is explicit.
        var saved = window.store.get(config.namedSchemasStorageKey);
        if (!saved) {
            return {};
        }

        var out = JSON.parse(saved);
        return out;
    }

    zato.mapper.schema.named.list = function() {

        var byName = readNamed();

        var out = [];
        for (var name in byName) {
            out.push(name);
        }
        out.sort();

        return out;
    };

    zato.mapper.schema.named.get = function(name) {
        var byName = readNamed();

        var out = byName[name];
        return out;
    };

    zato.mapper.schema.named.save = function(name, root) {
        var byName = readNamed();
        byName[name] = root;
        window.store.set(config.namedSchemasStorageKey, JSON.stringify(byName));
    };

    zato.mapper.schema.named.remove = function(name) {
        var byName = readNamed();
        delete byName[name];
        window.store.set(config.namedSchemasStorageKey, JSON.stringify(byName));
    };

})(jQuery);
