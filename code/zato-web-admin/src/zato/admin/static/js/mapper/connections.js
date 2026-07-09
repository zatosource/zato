
// Mapper kit - the connections model.
// Every mapping expressed as source paths and one target path - the one
// shared model behind the canvas badges and lines, the search filters,
// the per-field usage lists and the auto-map suggestions. A connection
// carries the selection of the row behind it, or null for the line an
// iteration scope itself draws between two repeating nodes.

(function($) {

    zato.mapper.connections = {};

// ////////////////////////////////////////////////////////////////////////

    // Extracts the source paths an expression references, by matching
    // its identifier tokens against the known path list.
    zato.mapper.connections.extractPaths = function(expression, pathList) {

        var out = [];

        var tokens = expression.match(/[A-Za-z_][\w.]*/g);
        if (tokens === null) {
            return out;
        }

        for (var tokenIdx = 0; tokenIdx < tokens.length; tokenIdx++) {
            var token = tokens[tokenIdx];
            if (pathList.indexOf(token) !== -1 && out.indexOf(token) === -1) {
                out.push(token);
            }
        }

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Returns [{sources, target, computed, conditioned, selection}] -
    // one entry per mapping row, with absolute paths on both sides.
    zato.mapper.connections.list = function(artifact) {

        var sourcePaths = zato.mapper.schema.listPaths(artifact.source_schema.root);

        var out = [];

        for (var rowIdx = 0; rowIdx < artifact.mappings.length; rowIdx++) {
            var row = artifact.mappings[rowIdx];
            var sources = zato.mapper.connections.extractPaths(row.expression, sourcePaths);

            out.push({
                sources: sources,
                target: row.target,
                computed: sources.length !== 1 || row.expression !== sources[0],
                conditioned: row.condition !== '',
                selection: {scopeIndex: null, rowIndex: rowIdx}
            });
        }

        for (var scopeIdx = 0; scopeIdx < artifact.scopes.length; scopeIdx++) {
            var scope = artifact.scopes[scopeIdx];

            // The scope itself connects the two repeating nodes ..
            out.push({
                sources: [scope.source],
                target: scope.target,
                computed: false,
                conditioned: false,
                selection: null
            });

            // .. and each child row connects relative paths, made
            // absolute here so badges and lines find their tree items.
            var scopeNode = zato.mapper.schema.nodeAtPath(artifact.source_schema.root, scope.source);
            var relativePaths = [];
            if (scopeNode !== null) {
                relativePaths = zato.mapper.schema.listPaths(scopeNode);
            }

            for (var childIdx = 0; childIdx < scope.mappings.length; childIdx++) {
                var childRow = scope.mappings[childIdx];
                var relativeSources = zato.mapper.connections.extractPaths(childRow.expression, relativePaths);

                var absoluteSources = [];
                for (var sourceIdx = 0; sourceIdx < relativeSources.length; sourceIdx++) {
                    absoluteSources.push(scope.source + '.' + relativeSources[sourceIdx]);
                }

                out.push({
                    sources: absoluteSources,
                    target: scope.target + '.' + childRow.target,
                    computed: relativeSources.length !== 1 || childRow.expression !== relativeSources[0],
                    conditioned: childRow.condition !== '',
                    selection: {scopeIndex: scopeIdx, rowIndex: childIdx}
                });
            }
        }

        return out;
    };

})(jQuery);
