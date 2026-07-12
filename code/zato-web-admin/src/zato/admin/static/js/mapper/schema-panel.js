
// Mapper kit - the schema panel.
// One controller per side (source or target): rendering the schema tree
// or a designed empty state.

(function($) {

    zato.mapper.schemaPanel = {};

// ////////////////////////////////////////////////////////////////////////

    var sideLabels = {source: 'source', target: 'target'};

// ////////////////////////////////////////////////////////////////////////

    // Initializes one schema column.
    // panelConfig:
    //   side:      'source' or 'target'
    //   store:     the artifact store instance
    //   body:      the column body element the tree renders into
    zato.mapper.schemaPanel.init = function(panelConfig) {

        var side = panelConfig.side;
        var store = panelConfig.store;
        var body = panelConfig.body;

        function schemaRoot() {
            var out = store.getArtifact()[side + '_schema'].root;
            return out;
        }

// ////////////////////////////////////////////////////////////////////////

        function renderEmptyState() {

            var wrapper = document.createElement('div');
            wrapper.className = 'mapper-empty-state';

            var title = document.createElement('h3');
            title.className = 'mapper-empty-state-title';
            title.textContent = 'No ' + sideLabels[side] + ' schema yet';
            wrapper.appendChild(title);

            var text = document.createElement('p');
            text.className = 'mapper-empty-state-text';
            text.textContent = 'Import a mapping document to see its schema here.';
            wrapper.appendChild(text);

            $(body).empty();
            body.appendChild(wrapper);
        }

// ////////////////////////////////////////////////////////////////////////

        function render() {

            var root = schemaRoot();

            if (root === null) {
                renderEmptyState();
            }
            else {
                zato.mapper.tree.render(body, root);
            }
        }

// ////////////////////////////////////////////////////////////////////////

        store.subscribe(render);

        render();
    };

})(jQuery);
