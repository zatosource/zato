
// Mapper kit - schema paths and tree edits.
// Every dotted path a schema tree contains, the fields behind them,
// deep copies, field renames and the nearest repeating ancestor -
// the helpers autocomplete, the filters, auto-map and the drop rules
// all navigate trees with.

(function($) {

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

})(jQuery);
