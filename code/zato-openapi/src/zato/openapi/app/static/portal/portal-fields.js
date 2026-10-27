zatoPortal.fields = {};

zatoPortal.fields.config = {
    inputTitle: 'Input',
    outputTitle: 'Output',
    requiredText: 'required',
    contentType: 'application/json',
    successStatus: '200',
    referencePrefix: '#/components/schemas/',
    anyType: 'any',
    nullType: 'null',
    arrayPrefix: 'array of ',
    alternativeSeparator: ' or ',
    enumSeparator: ', ',
    maxDepth: 4,
    indentStepRem: 1,
    indentUnit: 'rem',
    textIndent: '  ',
    columnGap: '  ',
    lineSeparator: '\n',
    blockSeparator: '\n\n',
    inputKey: 'input',
    outputKey: 'output',
    requiredClass: 'portal-chip portal-fields-required',
    typeClassPrefix: 'portal-fields-type portal-fields-type-',
    typeKinds: {
        'integer': 'number',
        'number': 'number',
        'int32': 'number',
        'int64': 'number',
        'float': 'number',
        'double': 'number',
        'boolean': 'boolean',
        'any': 'other',
    },
    modelPattern: /^[A-Z]/,
    modelKind: 'model',
    defaultKind: 'string',
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.build = function(operation) {

    var config = zatoPortal.fields.config;
    var container = zatoPortal.render.createElement('div', 'portal-operation-fields');

    var inputRows = zatoPortal.fields.collectInput(operation);
    var outputRows = zatoPortal.fields.collectOutput(operation);

    if(inputRows.length > 0) {
        var inputTable = zatoPortal.fields.buildTable(config.inputTitle, inputRows);
        container.appendChild(inputTable);
    }

    if(outputRows.length > 0) {
        var outputTable = zatoPortal.fields.buildTable(config.outputTitle, outputRows);
        container.appendChild(outputTable);
    }

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.collectInput = function(operation) {

    var config = zatoPortal.fields.config;
    var rows = [];
    var parameterNames = {};

    // Path and query string parameters come first ..
    if('parameters' in operation) {
        for(var parameterIndex = 0; parameterIndex < operation.parameters.length; parameterIndex++) {
            var parameter = operation.parameters[parameterIndex];
            var parameterType = zatoPortal.fields.describe(parameter.schema);

            rows.push({name: parameter.name, type: parameterType, isRequired: parameter.required, depth: 0});
            parameterNames[parameter.name] = true;
        }
    }

    // .. followed by the body, whose properties already listed as path parameters are not repeated.
    if('requestBody' in operation) {
        var content = operation.requestBody.content[config.contentType];
        zatoPortal.fields.collectProperties(content.schema, rows, 0, parameterNames, {});
    }

    return rows;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.getResponseMediaType = function(operation) {

    var response = operation.responses[zatoPortal.fields.config.successStatus];

    // An operation without output that requires no media type of its own documents no response content ..
    if(!('content' in response)) {
        return null;
    }

    // .. otherwise, its responses have one media type, JSON or the one that the endpoint requires.
    var out = Object.keys(response.content)[0];
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.collectOutput = function(operation) {

    var config = zatoPortal.fields.config;
    var rows = [];
    var mediaType = zatoPortal.fields.getResponseMediaType(operation);

    if(mediaType === null) {
        return rows;
    }

    var response = operation.responses[config.successStatus];
    var content = response.content[mediaType];

    // A media type that the endpoint requires has a schema only if the service has output
    if('schema' in content) {
        zatoPortal.fields.collectProperties(content.schema, rows, 0, {}, {});
    }

    return rows;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.getReferenceName = function(schema) {

    var reference = schema.$ref;

    var out = reference.slice(zatoPortal.fields.config.referencePrefix.length);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.getModelName = function(schema) {

    // A model is reached directly or as the element of an array
    if('$ref' in schema) {
        var out = zatoPortal.fields.getReferenceName(schema);
        return out;
    }

    if('items' in schema) {
        var items = schema.items;

        if('$ref' in items) {
            var itemsName = zatoPortal.fields.getReferenceName(items);
            return itemsName;
        }
    }

    return '';
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.collectProperties = function(schema, rows, depth, skippedNames, visited) {

    var config = zatoPortal.fields.config;
    var components = zatoPortal.state.components;
    var resolved = schema;

    if('$ref' in schema) {
        var referenceName = zatoPortal.fields.getReferenceName(schema);
        resolved = components[referenceName];
    }

    // Untyped input and output have no properties to list
    if(!('properties' in resolved)) {
        return;
    }

    var required = [];

    if('required' in resolved) {
        required = resolved.required;
    }

    var names = Object.keys(resolved.properties);

    for(var nameIndex = 0; nameIndex < names.length; nameIndex++) {
        var name = names[nameIndex];

        if(name in skippedNames) {
            continue;
        }

        var propertySchema = resolved.properties[name];
        var propertyType = zatoPortal.fields.describe(propertySchema);
        var isRequired = required.includes(name);

        rows.push({name: name, type: propertyType, isRequired: isRequired, depth: depth});

        // A nested model is listed under the property that holds it, once per branch and to a limited depth
        var modelName = zatoPortal.fields.getModelName(propertySchema);

        if(modelName === '') {
            continue;
        }

        if(modelName in visited) {
            continue;
        }

        if(depth >= config.maxDepth) {
            continue;
        }

        var branchVisited = Object.assign({}, visited);
        branchVisited[modelName] = true;

        var modelSchema = components[modelName];
        zatoPortal.fields.collectProperties(modelSchema, rows, depth + 1, {}, branchVisited);
    }
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.describe = function(schema) {

    var config = zatoPortal.fields.config;

    if('$ref' in schema) {
        var out = zatoPortal.fields.getReferenceName(schema);
        return out;
    }

    // A composed schema is any of its alternatives ..
    var alternatives = schema.anyOf;

    if(alternatives === undefined) {
        alternatives = schema.oneOf;
    }

    if(alternatives !== undefined) {
        var names = [];

        for(var alternativeIndex = 0; alternativeIndex < alternatives.length; alternativeIndex++) {
            var alternative = alternatives[alternativeIndex];
            var alternativeName = zatoPortal.fields.describe(alternative);
            names.push(alternativeName);
        }

        var joined = names.join(config.alternativeSeparator);
        return joined;
    }

    // .. an enumeration is its values ..
    if('enum' in schema) {
        var values = schema.enum.join(config.enumSeparator);
        return values;
    }

    // .. a format is more exact than a type ..
    if('format' in schema) {
        return schema.format;
    }

    if(!('type' in schema)) {
        return config.anyType;
    }

    // .. a nullable type is listed as the type it has when it is present ..
    var type = schema.type;

    if(Array.isArray(type)) {
        var types = type.filter(zatoPortal.fields.isNotNullType);
        type = types[0];
    }

    // .. and an array is described by its elements.
    if(type === 'array') {
        if('items' in schema) {
            var itemsType = zatoPortal.fields.describe(schema.items);
            var arrayType = config.arrayPrefix + itemsType;
            return arrayType;
        }
    }

    return type;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.isNotNullType = function(type) {
    var out = type !== zatoPortal.fields.config.nullType;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.buildTable = function(title, rows) {

    var config = zatoPortal.fields.config;
    var container = zatoPortal.render.createElement('div', 'portal-fields');

    var titleElement = zatoPortal.render.createElement('div', 'portal-panel-title portal-fields-title', title);
    container.appendChild(titleElement);

    var table = zatoPortal.render.createElement('table', 'portal-fields-table');
    var body = document.createElement('tbody');

    for(var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];
        var tableRow = document.createElement('tr');

        var nameCell = zatoPortal.render.createElement('td', 'portal-fields-name');

        // Properties of nested models are indented under the property that holds them
        var name = zatoPortal.render.createElement('span', 'portal-fields-name-text', row.name);
        var indent = row.depth * config.indentStepRem;
        name.style.marginLeft = indent + config.indentUnit;
        nameCell.appendChild(name);

        if(row.isRequired) {
            var required = zatoPortal.render.createElement('span', config.requiredClass, config.requiredText);
            nameCell.appendChild(required);
        }

        // Each type has the color its values have in the request and the response
        var typeKind = zatoPortal.fields.getTypeKind(row.type);
        var typeCell = zatoPortal.render.createElement('td', config.typeClassPrefix + typeKind, row.type);

        tableRow.appendChild(nameCell);
        tableRow.appendChild(typeCell);
        body.appendChild(tableRow);
    }

    table.appendChild(body);
    container.appendChild(table);

    return container;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.getTypeKind = function(type) {

    var config = zatoPortal.fields.config;
    var elementType = type;

    // An array is of the kind of its elements ..
    while(elementType.startsWith(config.arrayPrefix)) {
        elementType = elementType.slice(config.arrayPrefix.length);
    }

    if(elementType in config.typeKinds) {
        return config.typeKinds[elementType];
    }

    // .. a model is named after the schema it refers to, which starts with a capital letter ..
    if(config.modelPattern.test(elementType)) {
        return config.modelKind;
    }

    // .. and everything else, formats and enumerations included, is text.
    return config.defaultKind;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.toText = function(operation) {

    var config = zatoPortal.fields.config;
    var blocks = [];

    var inputRows = zatoPortal.fields.collectInput(operation);
    var outputRows = zatoPortal.fields.collectOutput(operation);

    if(inputRows.length > 0) {
        blocks.push(zatoPortal.fields.buildTextBlock(config.inputTitle, inputRows));
    }

    if(outputRows.length > 0) {
        blocks.push(zatoPortal.fields.buildTextBlock(config.outputTitle, outputRows));
    }

    var out = blocks.join(config.blockSeparator);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.buildTextBlock = function(title, rows) {

    var config = zatoPortal.fields.config;
    var names = [];
    var width = 0;

    // Nested properties are indented under the property that holds them, and every type starts in the same column
    for(var nameIndex = 0; nameIndex < rows.length; nameIndex++) {
        var row = rows[nameIndex];
        var name = config.textIndent.repeat(row.depth + 1) + row.name;

        names.push(name);
        width = Math.max(width, name.length);
    }

    var lines = [title];

    for(var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var line = names[rowIndex].padEnd(width) + config.columnGap + rows[rowIndex].type;

        if(rows[rowIndex].isRequired) {
            line += config.columnGap + config.requiredText;
        }

        lines.push(line);
    }

    var out = lines.join(config.lineSeparator);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.toJson = function(operation) {

    var config = zatoPortal.fields.config;

    var inputRows = zatoPortal.fields.collectInput(operation);
    var outputRows = zatoPortal.fields.collectOutput(operation);

    var value = {};
    value[config.inputKey] = zatoPortal.fields.nest(inputRows);
    value[config.outputKey] = zatoPortal.fields.nest(outputRows);

    var out = zatoPortal.highlight.format(value);
    return out;
};

// ////////////////////////////////////////////////////////////////////////

zatoPortal.fields.nest = function(rows) {

    // Our response to produce
    var out = [];

    // The rows of nested properties follow the row of the property that holds them, one level deeper
    var parents = [];

    for(var rowIndex = 0; rowIndex < rows.length; rowIndex++) {
        var row = rows[rowIndex];
        var field = {name: row.name, type: row.type, required: row.isRequired};

        while(parents.length > row.depth) {
            parents.pop();
        }

        if(parents.length === 0) {
            out.push(field);
        }
        else {
            var parent = parents[parents.length - 1];

            if(!('fields' in parent)) {
                parent.fields = [];
            }

            parent.fields.push(field);
        }

        parents.push(field);
    }

    return out;
};
