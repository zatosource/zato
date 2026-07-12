
// Mapper kit - the canvas hover behaviors.
// The gutter hover dims the lines with vertical proximity and lights
// up the one nearest the pointer, the field hover lights a field
// together with everything at the other end of its connections, and
// both share one way of lighting a row with its whole root-to-field
// path.

(function($) {

    zato.mapper.canvas.hover = {};

// ////////////////////////////////////////////////////////////////////////

    // How far above the topmost line or below the bottommost one the
    // dimming starts to ease in.
    var lineDimFadeDistance = 3 * zato.mapper.canvas.rootFontSize;

    // The opacity the lines dim to while the pointer sits amid them.
    var lineOpacityDimmed = 0.35;

    // How far towards grayscale the lines drain at the same time.
    var lineGrayscaleDimmed = 0.6;

// ////////////////////////////////////////////////////////////////////////

    zato.mapper.canvas.hover.setup = function(shared) {

        var canvasConfig = shared.config;
        var container = shared.container;
        var svg = shared.svg;

        // The resting opacity the token declares - the ceiling the
        // dimming eases back to as the pointer moves away.
        var lineOpacityResting = parseFloat(getComputedStyle(svg).getPropertyValue('--mapper-canvas-line-opacity'));

// ////////////////////////////////////////////////////////////////////////

        // Removing the inline properties lets the tokens' resting
        // values show through again.
        shared.clearDim = function() {
            svg.style.removeProperty('--mapper-canvas-line-opacity');
            svg.style.removeProperty('--mapper-canvas-line-grayscale');
        };

// ////////////////////////////////////////////////////////////////////////

        // Dims every line to the floor at once - the field hover and
        // the drag both push the lines back this way.
        shared.dimAll = function() {
            svg.style.setProperty('--mapper-canvas-line-opacity', lineOpacityDimmed);
            svg.style.setProperty('--mapper-canvas-line-grayscale', lineGrayscaleDimmed);
        };

// ////////////////////////////////////////////////////////////////////////

        // Eases the dimming in with vertical proximity to the lines -
        // strongest while the pointer is level with any of them, none
        // once it is further than the fade distance above the topmost
        // one or below the bottommost one.
        function applyDim(pointY) {

            var band = shared.lineBand();
            if (band === null) {
                shared.clearDim();
                return;
            }

            // How far the pointer is from the band - zero inside it.
            var distance = 0;
            if (pointY < band.top) {
                distance = band.top - pointY;
            }
            else if (pointY > band.bottom) {
                distance = pointY - band.bottom;
            }

            if (distance >= lineDimFadeDistance) {
                shared.clearDim();
                return;
            }

            var closeness = 1 - distance / lineDimFadeDistance;
            var opacity = lineOpacityResting - closeness * (lineOpacityResting - lineOpacityDimmed);
            var grayscale = closeness * lineGrayscaleDimmed;

            svg.style.setProperty('--mapper-canvas-line-opacity', opacity);
            svg.style.setProperty('--mapper-canvas-line-grayscale', grayscale);
        }

// ////////////////////////////////////////////////////////////////////////

        // Lights a row up together with its whole root-to-field path -
        // the class stands in for :hover on the item and on every
        // ancestor above it.
        shared.lightRow = function(row) {

            row.classList.add('mapper-tree-row-linked');

            var pathedItem = row.closest('.mapper-tree-item');
            while (pathedItem !== null) {
                pathedItem.classList.add('mapper-tree-item-pathed');
                pathedItem = pathedItem.parentElement.closest('.mapper-tree-item');
            }
        };

// ////////////////////////////////////////////////////////////////////////

        // The lit rows and their paths, cleared together in one place.
        shared.clearLinkedRows = function() {
            $(container).find('.mapper-tree-row-linked').removeClass('mapper-tree-row-linked');
            $(container).find('.mapper-tree-item-pathed').removeClass('mapper-tree-item-pathed');
        };

// ////////////////////////////////////////////////////////////////////////

        function clearGutterHover() {

            // The field hover owns the dimming and the lit rows while
            // it is active.
            if (!fieldHoverActive) {
                shared.clearDim();
                shared.clearLinkedRows();
            }

            container.style.cursor = '';

            var hoveredElements = svg.querySelectorAll('.mapper-canvas-line-hovered');
            for (var elementIdx = 0; elementIdx < hoveredElements.length; elementIdx++) {
                hoveredElements[elementIdx].classList.remove('mapper-canvas-line-hovered');
            }
        }

// ////////////////////////////////////////////////////////////////////////

        $(container).on('mousemove', function(event) {

            // A drag owns the lines - the ghost line dims them itself.
            if (shared.isDragActive()) {
                return;
            }

            // The dimming applies only inside the gutter - the trees
            // themselves keep their lines at full strength.
            if (!shared.isInGutter(event.clientX)) {
                clearGutterHover();
                return;
            }

            var containerRect = container.getBoundingClientRect();
            applyDim(event.clientY - containerRect.top);

            var lineId = shared.nearestLineId(event.clientX - containerRect.left, event.clientY - containerRect.top);

            var hoveredElements = svg.querySelectorAll('.mapper-canvas-line-hovered');
            for (var elementIdx = 0; elementIdx < hoveredElements.length; elementIdx++) {
                hoveredElements[elementIdx].classList.remove('mapper-canvas-line-hovered');
            }
            shared.clearLinkedRows();

            // A line under the pointer is clickable, so the cursor says so.
            container.style.cursor = lineId === null ? '' : 'pointer';

            if (lineId !== null) {
                var lineElements = svg.querySelectorAll('[data-line="' + lineId + '"]');
                for (var lineElementIdx = 0; lineElementIdx < lineElements.length; lineElementIdx++) {
                    lineElements[lineElementIdx].classList.add('mapper-canvas-line-hovered');
                }

                // The rows at both ends of the lit line light up with
                // their whole root-to-field paths, exactly like a
                // field hover lights them.
                var linePath = svg.querySelector('path[data-line="' + lineId + '"]');

                var hoveredSourceRow = shared.treeRowAt(canvasConfig.sourceBody, linePath.getAttribute('data-source-path'));
                if (hoveredSourceRow !== null) {
                    shared.lightRow(hoveredSourceRow);
                }

                var hoveredTargetRow = shared.treeRowAt(canvasConfig.targetBody, linePath.getAttribute('data-target-path'));
                if (hoveredTargetRow !== null) {
                    shared.lightRow(hoveredTargetRow);
                }
            }
        });

        $(container).on('mouseleave', clearGutterHover);

// ////////////////////////////////////////////////////////////////////////
// Field hover - the hovered field lights up together with every
// field at the other end of its connections and the lines between them,
// while all the other lines dim.
// ////////////////////////////////////////////////////////////////////////

        var fieldHoverActive = false;

        shared.clearFieldHover = function() {

            fieldHoverActive = false;
            shared.clearDim();
            shared.clearLinkedRows();

            var attachedElements = svg.querySelectorAll('.mapper-canvas-line-attached');
            for (var elementIdx = 0; elementIdx < attachedElements.length; elementIdx++) {
                attachedElements[elementIdx].classList.remove('mapper-canvas-line-attached');
            }
        };

// ////////////////////////////////////////////////////////////////////////

        function applyFieldHover(row, side) {

            shared.clearFieldHover();
            fieldHoverActive = true;

            row.classList.add('mapper-tree-row-linked');

            var fieldPath = row.closest('.mapper-tree-item').getAttribute('data-path');

            // The lines this field extends to or from - a field may sit
            // on several connections at once, so all of them count.
            var sideAttribute = side === 'source' ? 'data-source-path' : 'data-target-path';
            var otherAttribute = side === 'source' ? 'data-target-path' : 'data-source-path';
            var otherBody = side === 'source' ? canvasConfig.targetBody : canvasConfig.sourceBody;

            var linePaths = svg.querySelectorAll('path[' + sideAttribute + '="' + fieldPath + '"]');

            // An unconnected field lights up alone - there is nothing
            // to dim against.
            if (linePaths.length === 0) {
                return;
            }

            // Every line dims first, then the attached ones come back
            // to full strength through their own class.
            shared.dimAll();

            for (var lineIdx = 0; lineIdx < linePaths.length; lineIdx++) {
                var linePath = linePaths[lineIdx];

                // The line together with its endpoint dots.
                var lineId = linePath.getAttribute('data-line');
                var lineElements = svg.querySelectorAll('[data-line="' + lineId + '"]');
                for (var lineElementIdx = 0; lineElementIdx < lineElements.length; lineElementIdx++) {
                    lineElements[lineElementIdx].classList.add('mapper-canvas-line-attached');
                }

                // The field at the other end of this line, with its
                // whole root-to-field path lit the same way a direct
                // hover would light it.
                var otherRow = shared.treeRowAt(otherBody, linePath.getAttribute(otherAttribute));
                if (otherRow !== null) {
                    shared.lightRow(otherRow);
                }
            }
        }

// ////////////////////////////////////////////////////////////////////////

        $(canvasConfig.sourceBody).on('mouseenter', '.mapper-tree-row', function() {
            applyFieldHover(this, 'source');
        });

        $(canvasConfig.targetBody).on('mouseenter', '.mapper-tree-row', function() {
            applyFieldHover(this, 'target');
        });

        $(canvasConfig.sourceBody).on('mouseleave', '.mapper-tree-row', shared.clearFieldHover);
        $(canvasConfig.targetBody).on('mouseleave', '.mapper-tree-row', shared.clearFieldHover);
    };

})(jQuery);
