
// /////////////////////////////////////////////////////////////////////////////

// Weather map - the terrain. The field grid is painted sample by sample
// into a small image - bathymetry below the sea level, the land ramp above
// it, a hillshade lit from the upper left over the ground - and the browser
// stretches that image over the canvas bilinearly, which is what melts the
// samples into smooth shores and slopes.

$.fn.zato.weather_map.terrain = {};

// /////////////////////////////////////////////////////////////////////////////

(function() {

var terrain = $.fn.zato.weather_map.terrain;

// /////////////////////////////////////////////////////////////////////////////

terrain.config = {

    // How many colors each ramp is resolved into
    rampSize: 256,

    // How hard a slope lights or shades the ground it faces
    hillshadeStrength: 3.2,
    hillshadeMin: 0.72,
    hillshadeMax: 1.26
};

// /////////////////////////////////////////////////////////////////////////////

terrain.palette = {

    // The water, deepest basin to the shallows at the coast
    oceanStops: [
        {at: 0, color: '#0e3355'},
        {at: 0.5, color: '#1c5c86'},
        {at: 0.8, color: '#2f7ea6'},
        {at: 0.95, color: '#58a8bf'},
        {at: 1, color: '#8ecfd8'}
    ],

    // The ground, shoreline to the highest crest
    landStops: [
        {at: 0, color: '#d8c99a'},
        {at: 0.06, color: '#a8b072'},
        {at: 0.2, color: '#6a9552'},
        {at: 0.45, color: '#4f7d43'},
        {at: 0.65, color: '#8a9464'},
        {at: 0.85, color: '#b0a284'},
        {at: 1, color: '#e8e4d8'}
    ]
};

// /////////////////////////////////////////////////////////////////////////////

terrain.parseColor = function(color) {
    var red = parseInt(color.slice(1, 3), 16);
    var green = parseInt(color.slice(3, 5), 16);
    var blue = parseInt(color.slice(5, 7), 16);

    return [red, green, blue];
};

// /////////////////////////////////////////////////////////////////////////////

// One ramp resolved into a flat table of channels, so painting is
// a lookup rather than an interpolation per sample
terrain.buildRamp = function(stops) {
    var size = terrain.config.rampSize;
    var out = new Uint8ClampedArray(size * 3);

    var parsed = [];

    for(var stopIdx = 0; stopIdx < stops.length; stopIdx++) {
        parsed.push(terrain.parseColor(stops[stopIdx].color));
    }

    for(var entryIdx = 0; entryIdx < size; entryIdx++) {

        var position = entryIdx / (size - 1);

        // The pair of stops this position falls between
        var upperIdx = 1;

        while(upperIdx < stops.length - 1) {
            if(stops[upperIdx].at >= position) {
                break;
            }
            upperIdx += 1;
        }

        var lower = stops[upperIdx - 1];
        var upper = stops[upperIdx];

        var span = upper.at - lower.at;
        var blend = (position - lower.at) / span;

        var lowerColor = parsed[upperIdx - 1];
        var upperColor = parsed[upperIdx];

        var tableIdx = entryIdx * 3;

        out[tableIdx] = lowerColor[0] + (upperColor[0] - lowerColor[0]) * blend;
        out[tableIdx + 1] = lowerColor[1] + (upperColor[1] - lowerColor[1]) * blend;
        out[tableIdx + 2] = lowerColor[2] + (upperColor[2] - lowerColor[2]) * blend;
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The tallest ground of this world, which is what the land ramp is
// stretched up to - a quiet configuration stays readable rather than flat
terrain.maxElevation = function(grid) {
    var out = grid.seaLevel + 0.1;

    for(var sampleIdx = 0; sampleIdx < grid.elevation.length; sampleIdx++) {
        if(grid.elevation[sampleIdx] > out) {
            out = grid.elevation[sampleIdx];
        }
    }

    return out;
};

// /////////////////////////////////////////////////////////////////////////////

// The whole ground painted into the given context - one image sample per
// grid sample, stretched bilinearly over the full canvas
terrain.paint = function(context, model) {
    var config = terrain.config;
    var grid = model.grid;

    var seaLevel = grid.seaLevel;
    var rampTop = config.rampSize - 1;

    var oceanRamp = terrain.buildRamp(terrain.palette.oceanStops);
    var landRamp = terrain.buildRamp(terrain.palette.landStops);

    var highest = terrain.maxElevation(grid);
    var landSpan = highest - seaLevel;

    var image = new ImageData(grid.columns, grid.rows);
    var pixels = image.data;

    for(var sampleIdx = 0; sampleIdx < grid.elevation.length; sampleIdx++) {

        var elevation = grid.elevation[sampleIdx];

        var red = 0;
        var green = 0;
        var blue = 0;

        if(elevation < seaLevel) {

            // Below the sea level the color reads the depth
            var depth = (seaLevel - elevation) / seaLevel;

            if(depth > 1) {
                depth = 1;
            }

            var oceanIdx = Math.round((1 - depth) * rampTop) * 3;

            red = oceanRamp[oceanIdx];
            green = oceanRamp[oceanIdx + 1];
            blue = oceanRamp[oceanIdx + 2];
        }
        else {

            // Above it the color reads the height, and the slope against
            // the light models the relief
            var height = (elevation - seaLevel) / landSpan;

            if(height > 1) {
                height = 1;
            }

            var landIdx = Math.round(height * rampTop) * 3;

            var shade = 1 + (grid.slopeX[sampleIdx] + grid.slopeY[sampleIdx]) * config.hillshadeStrength;

            if(shade < config.hillshadeMin) {
                shade = config.hillshadeMin;
            }
            if(shade > config.hillshadeMax) {
                shade = config.hillshadeMax;
            }

            red = landRamp[landIdx] * shade;
            green = landRamp[landIdx + 1] * shade;
            blue = landRamp[landIdx + 2] * shade;
        }

        var pixelIdx = sampleIdx * 4;

        pixels[pixelIdx] = red;
        pixels[pixelIdx + 1] = green;
        pixels[pixelIdx + 2] = blue;
        pixels[pixelIdx + 3] = 255;
    }

    // The small image goes onto its own canvas first, because only a canvas
    // can be drawn stretched and smoothed onto another
    var scratch = document.createElement('canvas');
    scratch.width = grid.columns;
    scratch.height = grid.rows;

    var scratchContext = scratch.getContext('2d');
    scratchContext.putImageData(image, 0, 0);

    context.imageSmoothingEnabled = true;
    context.drawImage(scratch, 0, 0, grid.columns * grid.step, grid.rows * grid.step);
};

// /////////////////////////////////////////////////////////////////////////////

})();
