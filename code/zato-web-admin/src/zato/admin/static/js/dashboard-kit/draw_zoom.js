
/* Dashboard kit - how closely an SVG drawing is looked at.
   Ctrl and the wheel over the room a drawing has draws it larger or smaller.
   The drawing alone is made larger by it, nothing else on the page, so
   everything around it stays where it was put and the drawing scrolls inside
   its own room once it no longer fits.

   The drawing is laid out once by its own page and drawn at whatever size it
   is being looked at, so every shape and every word in it keeps its
   proportions. How large it was left is kept by the browser under the page's
   own storage key and is how large the next drawing comes up.

   Each page creates an instance of its own - the element that answers to the
   wheel, the storage key and an optional logger are the instance's config. */

(function() {
    var ns = $.fn.zato.dashboard_kit;
    ns.draw_zoom = {};

    ns.draw_zoom.defaults = {

        /* What one turn of the wheel does to how large the drawing is drawn,
           and how far that may be taken either way */
        step: 1.1,
        least: 0.4,
        most: 3,

        /* The size a drawing is drawn at until it is looked at closer */
        plain: 1
    };

    /* ------------------------------------------------------------ */

    /* Config carries `host` - a function returning the element the wheel is
       listened on and the drawing's svg lives in - `storage_key`, and an
       optional `log(name, details)` callback. */
    ns.draw_zoom.create = function(config) {
        var defaults = ns.draw_zoom.defaults;

        var zoom = {
            state: {

                /* How large the drawing is drawn against how large it was laid
                   out, and the size it was laid out at, which is what that is
                   measured off */
                level: defaults.plain,
                baseWidth: 0,
                baseHeight: 0
            }
        };

        /* ------------------------------------------------------------ */

        zoom.clamp = function(level) {
            if(level < defaults.least) {
                return defaults.least;
            }

            if(level > defaults.most) {
                return defaults.most;
            }

            return level;
        };

        /* ------------------------------------------------------------ */

        /* How large the drawing was last looked at, which is how large it is
           drawn on the next visit. */
        zoom.read = function() {
            var kept = Number(window.localStorage.getItem(config.storage_key));

            /* Nothing kept yet, or something kept that is no size at all */
            if(!kept) {
                return defaults.plain;
            }

            return zoom.clamp(kept);
        };

        /* ------------------------------------------------------------ */

        /* The size the drawing was laid out at, which every size it is then
           drawn at is measured off. */
        zoom.remember = function(width, height) {
            zoom.state.baseWidth = width;
            zoom.state.baseHeight = height;
        };

        /* ------------------------------------------------------------ */

        /* The drawing at the size it is being looked at. The shapes are drawn
           to the room the drawing is given rather than laid out again, so what
           is on screen only grows or shrinks. */
        zoom.apply = function() {
            var svg = config.host().querySelector('svg');

            /* No drawing on screen yet */
            if(svg === null) {
                return;
            }

            svg.style.width = (zoom.state.baseWidth * zoom.state.level) + 'px';
            svg.style.height = (zoom.state.baseHeight * zoom.state.level) + 'px';
        };

        /* ------------------------------------------------------------ */

        /* Ctrl and the wheel is how a drawing is looked at closer or further
           off. The browser reads that as the whole page being made larger,
           which is not what is being asked for here, so that reading is turned
           down and the drawing alone answers. */
        zoom.onWheel = function(event) {

            /* The wheel on its own scrolls the room the drawing is in */
            if(!event.ctrlKey) {
                return;
            }

            event.preventDefault();

            var isCloser = event.deltaY < 0;
            var step = isCloser ? defaults.step : 1 / defaults.step;
            var level = zoom.clamp(zoom.state.level * step);

            /* As close, or as far off, as the drawing goes */
            if(level === zoom.state.level) {
                return;
            }

            zoom.state.level = level;
            window.localStorage.setItem(config.storage_key, String(level));

            if(config.log) {
                config.log('draw_zoom.onWheel', {
                    isCloser: isCloser,
                    level: level,
                    baseWidth: zoom.state.baseWidth,
                    baseHeight: zoom.state.baseHeight
                });
            }

            zoom.apply();
        };

        /* ------------------------------------------------------------ */

        zoom.init = function() {

            /* The whole of the room the drawing has answers to the wheel, not
               only the shapes in it */
            config.host().addEventListener('wheel', zoom.onWheel, {passive: false});

            zoom.state.level = zoom.read();
        };

        return zoom;
    };

})();
