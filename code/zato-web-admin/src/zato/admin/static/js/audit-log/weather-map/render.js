
// /////////////////////////////////////////////////////////////////////////////

// Weather map - the composition. The world is painted once into an offscreen
// base - terrain, depth contours, the coastline, the names, the cities - and
// every frame on the screen is that base plus whatever the pointer is doing.
// Highlights of fused landmasses are soft tints of the owned ground, built
// lazily and kept until the world itself changes.

$.fn.zato.weather_map.render = {};

// /////////////////////////////////////////////////////////////////////////////

(function() {

var coast = $.fn.zato.weather_map.coast;
var render = $.fn.zato.weather_map.render;
var terrain = $.fn.zato.weather_map.terrain;

// /////////////////////////////////////////////////////////////////////////////

render.config = {

    // The backing store is drawn at twice the logical size and scaled down,
    // which is what keeps the coastlines crisp on any screen
    pixelRatio: 2,

    coastWidth: 1.25,

    // Where the depth contours run, as shares of the sea level
    depthShares: [0.6, 0.3],
    depthContourWidth: 1,

    cityDotRadius: 3,
    cityHaloRadius: 5,
    cityRingRadius: 9,
    cityRingWidth: 1.75,

    cityFont: '11px Roboto Mono, monospace',
    cityLabelOffsetX: 10,
    cityLabelOffsetY: 4,
    cityLabelHaloWidth: 3,

    // Past this many cities on one continent the names come off the map
    // and live in the cards alone
    labelMaxCities: 40,

    continentFont: 'Roboto Mono, monospace',
    continentFontMin: 15,
    continentFontMax: 40,
    continentFontScale: 0.3,

    // The graticule - the faint grid that makes the frame read as a chart
    // of a planet rather than an arbitrary crop
    graticuleSpacing: 110,
    graticuleWidth: 1,

    // How deep the polar ice fringes reach in from the top and bottom edges
    iceDepth: 46,

    vignetteInnerRadius: 0.6
};

// /////////////////////////////////////////////////////////////////////////////

render.palette = {

    coastline: 'rgba(15, 45, 60, 0.55)',
    depthContour: 'rgba(220, 240, 245, 0.16)',

    continentLabel: 'rgba(25, 40, 35, 0.3)',

    cityDot: '#153a5e',
    cityHalo: 'rgba(255, 255, 255, 0.85)',

    cityLabel: '#1f2d33',
    cityLabelHalo: 'rgba(255, 255, 255, 0.7)',

    cityRingHover: 'rgba(20, 45, 60, 0.85)',
    cityRingPinned: 'rgb(246, 166, 5)',

    // The channels a hover and a pinned tint write into their masks
    tintHover: [255, 255, 255, 46],
    tintPinned: [246, 166, 5, 66],

    graticule: 'rgba(235, 243, 246, 0.07)',
    ice: 'rgba(240, 248, 252, 0.22)',

    vignette: 'rgba(20, 40, 50, 0.25)'
};

// /////////////////////////////////////////////////////////////////////////////

// The base the screen is composed from - built on load and on resize,
// then only ever copied - and the tint masks grown on demand beside it
render.baseCanvas = null;
render.tintCache = {};

// /////////////////////////////////////////////////////////////////////////////

// Each type's name written across its own share of the land
render.drawContinentLabels = function(context, model) {
    var config = render.config;

    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillStyle = render.palette.continentLabel;
    context.letterSpacing = '2px';

    for(var continentIdx = 0; continentIdx < model.continents.length; continentIdx++) {
        var continent = model.continents[continentIdx];

        var fontSize = continent.radius * config.continentFontScale;

        if(fontSize < config.continentFontMin) {
            fontSize = config.continentFontMin;
        }
        if(fontSize > config.continentFontMax) {
            fontSize = config.continentFontMax;
        }

        context.font = '600 ' + fontSize + 'px ' + config.continentFont;
        context.fillText(continent.label.toUpperCase(), continent.labelX, continent.labelY);
    }

    context.letterSpacing = '0px';
};

// /////////////////////////////////////////////////////////////////////////////

// Every city - a dark dot on a light halo so it reads on any ground, and,
// while the continent has room for them, its name beside it
render.drawCities = function(context, model) {
    var config = render.config;

    context.textAlign = 'left';
    context.textBaseline = 'middle';
    context.font = config.cityFont;
    context.lineJoin = 'round';

    for(var continentIdx = 0; continentIdx < model.continents.length; continentIdx++) {
        var continent = model.continents[continentIdx];

        var withLabels = continent.cities.length <= config.labelMaxCities;

        for(var cityIdx = 0; cityIdx < continent.cities.length; cityIdx++) {
            var city = continent.cities[cityIdx];

            context.fillStyle = render.palette.cityHalo;
            context.beginPath();
            context.arc(city.x, city.y, config.cityHaloRadius, 0, Math.PI * 2);
            context.fill();

            context.fillStyle = render.palette.cityDot;
            context.beginPath();
            context.arc(city.x, city.y, config.cityDotRadius, 0, Math.PI * 2);
            context.fill();

            if(withLabels) {

                var labelX = city.x + config.cityLabelOffsetX;
                var labelY = city.y + config.cityLabelOffsetY;

                context.strokeStyle = render.palette.cityLabelHalo;
                context.lineWidth = config.cityLabelHaloWidth;
                context.strokeText(city.name, labelX, labelY);

                context.fillStyle = render.palette.cityLabel;
                context.fillText(city.name, labelX, labelY);
            }
        }
    }
};

// /////////////////////////////////////////////////////////////////////////////

// The faint grid of meridians and parallels - the frame reads as a chart
// of a planet rather than an arbitrary crop
render.drawGraticule = function(context, model) {
    var config = render.config;

    context.strokeStyle = render.palette.graticule;
    context.lineWidth = config.graticuleWidth;

    context.beginPath();

    for(var lineX = config.graticuleSpacing; lineX < model.width; lineX += config.graticuleSpacing) {
        context.moveTo(lineX, 0);
        context.lineTo(lineX, model.height);
    }

    for(var lineY = config.graticuleSpacing; lineY < model.height; lineY += config.graticuleSpacing) {
        context.moveTo(0, lineY);
        context.lineTo(model.width, lineY);
    }

    context.stroke();
};

// /////////////////////////////////////////////////////////////////////////////

// The polar fringes - a wash of ice along the top and bottom edges, so
// the frame's limits read as latitudes and not as a cut
render.drawIce = function(context, model) {
    var depth = render.config.iceDepth;
    var ice = render.palette.ice;

    var top = context.createLinearGradient(0, 0, 0, depth);
    top.addColorStop(0, ice);
    top.addColorStop(1, 'rgba(240, 248, 252, 0)');

    context.fillStyle = top;
    context.fillRect(0, 0, model.width, depth);

    var bottom = context.createLinearGradient(0, model.height, 0, model.height - depth);
    bottom.addColorStop(0, ice);
    bottom.addColorStop(1, 'rgba(240, 248, 252, 0)');

    context.fillStyle = bottom;
    context.fillRect(0, model.height - depth, model.width, depth);
};

// /////////////////////////////////////////////////////////////////////////////

// The light falling off toward the edges, which is what keeps the eye
// on the map
render.drawVignette = function(context, model) {
    var centerX = model.width / 2;
    var centerY = model.height / 2;

    var outerRadius = Math.sqrt(centerX * centerX + centerY * centerY);
    var innerRadius = outerRadius * render.config.vignetteInnerRadius;

    var gradient = context.createRadialGradient(centerX, centerY, innerRadius, centerX, centerY, outerRadius);
    gradient.addColorStop(0, 'rgba(0, 0, 0, 0)');
    gradient.addColorStop(1, render.palette.vignette);

    context.fillStyle = gradient;
    context.fillRect(0, 0, model.width, model.height);
};

// /////////////////////////////////////////////////////////////////////////////

// The whole base - terrain, depth lines, the coastline, names, cities and
// the vignette, drawn once into an offscreen canvas the screen copies from
render.buildBase = function(model) {
    var config = render.config;
    var grid = model.grid;

    var canvas = document.createElement('canvas');
    canvas.width = model.width * config.pixelRatio;
    canvas.height = model.height * config.pixelRatio;

    var context = canvas.getContext('2d');
    context.scale(config.pixelRatio, config.pixelRatio);

    terrain.paint(context, model);

    // The depth lines first, under everything the land carries
    context.strokeStyle = render.palette.depthContour;
    context.lineWidth = config.depthContourWidth;

    for(var depthIdx = 0; depthIdx < config.depthShares.length; depthIdx++) {
        var threshold = grid.seaLevel * config.depthShares[depthIdx];
        context.stroke(coast.buildPath(grid, threshold));
    }

    context.strokeStyle = render.palette.coastline;
    context.lineWidth = config.coastWidth;
    context.stroke(coast.coastline(grid));

    render.drawGraticule(context, model);
    render.drawIce(context, model);

    render.drawContinentLabels(context, model);
    render.drawCities(context, model);
    render.drawVignette(context, model);

    render.baseCanvas = canvas;
    render.tintCache = {};
};

// /////////////////////////////////////////////////////////////////////////////

// The soft tint of one continent's ground - grown at the grid's own
// resolution and stretched smooth, then kept for as long as the world stands
render.tintMask = function(model, continentIdx, kind) {
    var key = continentIdx + '-' + kind;

    if(key in render.tintCache) {
        return render.tintCache[key];
    }

    var grid = model.grid;
    var seaLevel = grid.seaLevel;

    var channels = kind === 'pinned' ? render.palette.tintPinned : render.palette.tintHover;

    var image = new ImageData(grid.columns, grid.rows);
    var pixels = image.data;

    for(var sampleIdx = 0; sampleIdx < grid.elevation.length; sampleIdx++) {

        if(grid.owner[sampleIdx] !== continentIdx) {
            continue;
        }
        if(grid.elevation[sampleIdx] < seaLevel) {
            continue;
        }

        var pixelIdx = sampleIdx * 4;

        pixels[pixelIdx] = channels[0];
        pixels[pixelIdx + 1] = channels[1];
        pixels[pixelIdx + 2] = channels[2];
        pixels[pixelIdx + 3] = channels[3];
    }

    var mask = document.createElement('canvas');
    mask.width = grid.columns;
    mask.height = grid.rows;

    var maskContext = mask.getContext('2d');
    maskContext.putImageData(image, 0, 0);

    render.tintCache[key] = mask;

    return mask;
};

// /////////////////////////////////////////////////////////////////////////////

render.drawTint = function(context, model, continentIdx, kind) {
    var grid = model.grid;

    var mask = render.tintMask(model, continentIdx, kind);

    context.imageSmoothingEnabled = true;
    context.drawImage(mask, 0, 0, grid.columns * grid.step, grid.rows * grid.step);
};

// /////////////////////////////////////////////////////////////////////////////

// A ring around one city - what the pointer resting on it and a pinned
// choice both wear, each in its own ink
render.drawCityRing = function(context, city, strokeStyle) {
    var config = render.config;

    context.strokeStyle = strokeStyle;
    context.lineWidth = config.cityRingWidth;

    context.beginPath();
    context.arc(city.x, city.y, config.cityRingRadius, 0, Math.PI * 2);
    context.stroke();
};

// /////////////////////////////////////////////////////////////////////////////

// Which continent of the model a hit rests on
render.hitContinentIdx = function(model, hit) {

    for(var continentIdx = 0; continentIdx < model.continents.length; continentIdx++) {
        if(model.continents[continentIdx] === hit.continent) {
            return continentIdx;
        }
    }

    return -1;
};

// /////////////////////////////////////////////////////////////////////////////

// One frame on the screen - the base, then whatever the pointer or a pinned
// choice adds on top of it
render.drawScene = function(context, model, state) {
    var ratio = render.config.pixelRatio;

    context.setTransform(1, 0, 0, 1, 0, 0);
    context.drawImage(render.baseCanvas, 0, 0);

    context.setTransform(ratio, 0, 0, ratio, 0, 0);

    // The pinned choice paints under the hover, so a pointer passing over
    // something else never hides what was chosen
    if(state.pinned) {
        if(state.pinned.kind === 'city') {
            render.drawCityRing(context, state.pinned.city, render.palette.cityRingPinned);
        }
        else {
            render.drawTint(context, model, render.hitContinentIdx(model, state.pinned), 'pinned');
        }
    }

    if(state.hover) {
        if(state.hover.kind === 'city') {
            render.drawCityRing(context, state.hover.city, render.palette.cityRingHover);
        }
        else {
            render.drawTint(context, model, render.hitContinentIdx(model, state.hover), 'hover');
        }
    }
};

// /////////////////////////////////////////////////////////////////////////////

})();
