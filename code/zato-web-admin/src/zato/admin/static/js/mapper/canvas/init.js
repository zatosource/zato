
// Mapper kit - the mapping canvas.
// Drag a field from either tree onto the other to create a mapping row.
// Dropping a leaf under a repeating node onto a leaf under another
// repeating node creates an iteration scope automatically and the
// children map relatively. An SVG layer always draws every
// connection line.
// While the pointer is over the gutter where the lines live, they dim
// gradually - the closer the pointer comes to them vertically, the
// dimmer they get - except the one under the pointer, which lights up
// with a marching-ants animation. Lines are interactive: a click selects the
// mapping row a line belongs to, a right-click opens a menu over it,
// and right-clicking a target field offers wrapping its expression in
// a function or setting a constant value on an unmapped field.
//
// The implementation spreads over the canvas/ files - lines, drops,
// hover, drag and menus - each contributing its part to one shared
// context object this file assembles and wires together.

(function($) {

    zato.mapper.canvas = {};

// ////////////////////////////////////////////////////////////////////////

    // Interaction distances scale with the root font size, so they
    // follow the user's font and display settings instead of being
    // fixed pixel counts - the other canvas files derive their
    // distances from this one value.
    zato.mapper.canvas.rootFontSize = parseFloat(getComputedStyle(document.documentElement).fontSize);

// ////////////////////////////////////////////////////////////////////////

    // Initializes the canvas.
    // canvasConfig:
    //   store:         the artifact store
    //   container:     the columns container the SVG layer covers
    //   sourceColumn:  the source column element
    //   targetColumn:  the target column element
    //   sourceBody:    the source tree body
    //   targetBody:    the target tree body
    //   svg:           the SVG element of the line layer
    //   onRowCreated:  called with {scopeIndex, rowIndex} after a drop
    //   onRowOpen:     called with ({scopeIndex, rowIndex}, field) when a
    //                  line or a menu entry asks for the row - field is
    //                  '' or the detail field to focus ('expression',
    //                  'condition', 'default')
    //   onDeselect:    called when a click lands on empty gutter space
    //   onNotice:      called with the reason whenever a drop is refused
    //   onStructureDrop: called with (sourcePath, targetPath) when one
    //                  structure is dropped onto another - the page opens
    //                  the scoped auto-map suggestions over the pair
    //   onRenameField: called with (side, path) when a tree menu asks
    //                  for a field rename
    // Returns {redraw}.
    zato.mapper.canvas.init = function(canvasConfig) {

        // The context the canvas files share - each setup call below
        // adds its own functions to it and reads the others' through it.
        var shared = {
            config: canvasConfig,
            store: canvasConfig.store,
            container: canvasConfig.container,
            svg: canvasConfig.svg,

            // The connections behind the lines drawn most recently -
            // the click, hover and menu handlers all look lines up here.
            lastConnections: []
        };

        zato.mapper.canvas.lines.setup(shared);
        zato.mapper.canvas.drops.setup(shared);
        zato.mapper.canvas.hover.setup(shared);
        zato.mapper.canvas.drag.setup(shared);
        zato.mapper.canvas.menus.setup(shared);

        // Lines track the trees: store changes re-render them, scrolling
        // and column resizes move their rows.
        shared.store.subscribe(shared.redraw);

        $(canvasConfig.sourceBody).on('scroll', shared.redraw);
        $(canvasConfig.targetBody).on('scroll', shared.redraw);
        $(window).on('resize', shared.redraw);

        var observer = new ResizeObserver(shared.redraw);
        observer.observe(canvasConfig.sourceColumn);
        observer.observe(canvasConfig.targetColumn);

        shared.redraw();

        return {redraw: shared.redraw};
    };

})(jQuery);
