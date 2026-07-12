
// Mapper - browser assertions for the schema module.
// Inference from an example, the JSON Schema importer, scaffolding,
// named schemas and path listing.

(function($) {

    var check = zato.mapper.assertions.check;
    var checkEqual = zato.mapper.assertions.checkEqual;
    var fieldByName = zato.mapper.assertions.fieldByName;

// ////////////////////////////////////////////////////////////////////////
// Schema inference
// ////////////////////////////////////////////////////////////////////////

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

    runInferenceAssertions();
    runJSONSchemaAssertions();
    runScaffoldAssertions();
    runNamedSchemaAssertions();
    runPathListingAssertions();

})(jQuery);
