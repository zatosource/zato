
// Mapper kit - schema tree renderer.
// Renders one schema tree into a container: field names, type badges,
// cardinality badges for repeating nodes, optional markers and format
// hints, with expand and collapse on every container node.

(function($) {

    zato.mapper.tree = {};

    // Assigned by the page bootstrap so collapsing or expanding a
    // branch redraws the connection lines, whose rows have just moved.
    zato.mapper.tree.onLayoutChanged = null;

    // Set by the canvas when a drag ends, so the click the drag
    // releases does not also toggle the row it started on.
    zato.mapper.tree.suppressNextToggle = false;

// ////////////////////////////////////////////////////////////////////////

    function typeLabelOf(node) {
        if (node.kind === 'object') {
            return 'object';
        }
        if (node.kind === 'array') {
            return typeLabelOf(node.element);
        }

        var out = node.types.join(' | ');
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function typeClassOf(node) {
        if (node.kind === 'object') {
            return 'object';
        }
        if (node.kind === 'array') {
            return typeClassOf(node.element);
        }
        if (node.types.length > 1) {
            return 'union';
        }

        var out = node.types[0];
        return out;
    }

// ////////////////////////////////////////////////////////////////////////

    function buildBadges(node, optional) {

        var badges = document.createElement('span');
        badges.className = 'mapper-tree-badges';

        // A repeating node carries a cardinality badge ..
        if (node.kind === 'array') {
            var cardinality = document.createElement('span');
            cardinality.className = 'dashboard-outcome-badge mapper-tree-cardinality-badge';
            cardinality.textContent = 'list';
            badges.appendChild(cardinality);
        }

        // .. every node carries a type badge ..
        var typeBadge = document.createElement('span');
        typeBadge.className = 'dashboard-outcome-badge mapper-tree-type-badge mapper-tree-type-' + typeClassOf(node);
        typeBadge.textContent = typeLabelOf(node);
        badges.appendChild(typeBadge);

        // .. a format hint is display metadata next to the type ..
        var formatNode = node;
        if (node.kind === 'array') {
            formatNode = node.element;
        }
        if (formatNode.kind === 'leaf') {
            if (formatNode.format !== '') {
                var format = document.createElement('span');
                format.className = 'dashboard-outcome-badge mapper-tree-format-badge';
                format.textContent = formatNode.format;
                format.setAttribute('data-tippy-content', 'The values of this field use the ' + formatNode.format + ' format');
                badges.appendChild(format);
            }
        }

        // .. and optional fields are marked as such.
        if (optional) {
            var optionalBadge = document.createElement('span');
            optionalBadge.className = 'dashboard-outcome-badge mapper-tree-optional-badge';
            optionalBadge.textContent = 'optional';
            optionalBadge.setAttribute('data-tippy-content', 'An optional field - it may be absent from the data');
            badges.appendChild(optionalBadge);
        }

        return badges;
    }

// ////////////////////////////////////////////////////////////////////////

    function childFieldsOf(node) {

        // The children shown under a node: an object shows its fields,
        // an array shows the fields of its element object.
        if (node.kind === 'object') {
            return node.fields;
        }
        if (node.kind === 'array') {
            if (node.element.kind === 'object') {
                return node.element.fields;
            }
        }

        return [];
    }

// ////////////////////////////////////////////////////////////////////////

    function buildFieldItem(field, path) {

        var item = document.createElement('li');
        item.className = 'mapper-tree-item';
        item.setAttribute('data-path', path);

        var row = document.createElement('div');
        row.className = 'mapper-tree-row';
        row.setAttribute('tabindex', '0');

        var childFields = childFieldsOf(field.node);
        var hasChildren = childFields.length > 0;

        // A container node gets a toggle, a leaf gets a spacer
        // so names always line up. The chevron is one SVG the CSS
        // rotates when the item collapses.
        var toggle = document.createElement('span');
        if (hasChildren) {
            toggle.className = 'mapper-tree-toggle';
            var chevron = document.createElement('i');
            chevron.setAttribute('data-lucide', 'chevron-down');
            toggle.appendChild(chevron);
        }
        else {
            toggle.className = 'mapper-tree-toggle-spacer';
        }
        row.appendChild(toggle);

        var name = document.createElement('span');
        name.className = 'mapper-tree-name';
        name.textContent = field.name;
        row.appendChild(name);

        var badges = buildBadges(field.node, field.optional);
        row.appendChild(badges);

        item.appendChild(row);

        if (hasChildren) {
            var childList = document.createElement('ul');
            childList.className = 'mapper-tree-children';

            for (var childIdx = 0; childIdx < childFields.length; childIdx++) {
                var childField = childFields[childIdx];
                var childItem = buildFieldItem(childField, path + '.' + childField.name);
                childList.appendChild(childItem);
            }

            item.appendChild(childList);

            // Clicking anywhere on a container row - the name included -
            // collapses or expands its children. The collapsed class
            // alone drives the chevron rotation.
            $(row).on('click', function() {

                // The click a drag releases is not a toggle.
                if (zato.mapper.tree.suppressNextToggle) {
                    zato.mapper.tree.suppressNextToggle = false;
                    return;
                }

                $(item).toggleClass('mapper-tree-item-collapsed');
                zato.mapper.tree.onLayoutChanged();
            });
        }

        return item;
    }

// ////////////////////////////////////////////////////////////////////////

    // Renders a schema tree into the container. The root is an object
    // node whose fields become the top-level rows, or an array node
    // whose element fields do.
    zato.mapper.tree.render = function(container, root) {

        var list = document.createElement('ul');
        list.className = 'mapper-tree';

        var fields = childFieldsOf(root);
        for (var fieldIdx = 0; fieldIdx < fields.length; fieldIdx++) {
            var field = fields[fieldIdx];
            var item = buildFieldItem(field, field.name);
            list.appendChild(item);
        }

        $(container).empty();
        container.appendChild(list);

        // The chevron placeholders become inline SVGs and every badge
        // gets its explanatory tooltip.
        lucide.createIcons();
        tippy(container.querySelectorAll('[data-tippy-content]'), {theme: 'dark', arrow: true});
    };

})(jQuery);
