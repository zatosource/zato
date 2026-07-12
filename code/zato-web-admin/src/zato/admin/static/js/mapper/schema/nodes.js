
// Mapper kit - schema nodes and inference.
// Node constructors, string format detection, sample merging and
// inference from a pasted JSON example. The importer, the scaffolding,
// the path helpers and the named schemas live in the other schema/ files.

(function($) {

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

})(jQuery);
