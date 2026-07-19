
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Syntax highlighting for the invoker panes - the raw textareas get a colored
// overlay behind their transparent text and the parsed view of an HL7 payload
// gets its colored HTML built line by line.

$.fn.zato.ide.highlight = {};

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.highlight.config = {

    // Which panes carry a highlighted overlay
    "pane_names": ["request", "response"],

    // What an ER7 segment line looks like - a three-character segment id
    // followed by the field separator
    "er7_line_pattern": /^[A-Z][A-Z0-9]{2}\|/,

    // The separators of ER7 values - fields, components, repetitions and subcomponents
    "er7_separator_pattern": /[|^~&]/g,

    // The JSON tokens - a string with an optional key colon, a number,
    // a keyword or a piece of punctuation
    "json_token_pattern": /("(?:\\.|[^"\\])*")(\s*:)?|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|\b(true|false|null)\b|([{}\[\],:])/g,

    // The header line of HL7's parsed text - the message type and its control id
    "parsed_header_pattern": /^(\S+) \(control id (.*)\)$/,

    // A segment id alone on a line of HL7's parsed text
    "parsed_segment_pattern": /^[A-Z][A-Z0-9]{2}$/,

    // A field or component line of HL7's parsed text - indent, reference, label and value
    "parsed_field_pattern": /^(\s+)(\S+)  (.*?): (.*)$/,
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

// The characters that must not reach the overlay as markup.
$.fn.zato.ide.highlight.escape = function(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Runs one token pattern over raw text and builds HTML out of it - each token
// goes through the given wrapper and everything in between is escaped plain text.
$.fn.zato.ide.highlight.replace_tokens = function(text, pattern, wrap_match) {

    let out = "";
    let last_index = 0;

    // The pattern is shared, so each run starts from the top
    pattern.lastIndex = 0;

    var match;

    while((match = pattern.exec(text)) !== null) {

        let plain = text.slice(last_index, match.index);
        out += $.fn.zato.ide.highlight.escape(plain);
        out += wrap_match(match);

        last_index = match.index + match[0].length;
    }

    out += $.fn.zato.ide.highlight.escape(text.slice(last_index));
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One ER7 value with its separators colored.
$.fn.zato.ide.highlight.er7_value_to_html = function(text) {

    let wrap_match = function(match) {
        let separator = $.fn.zato.ide.highlight.escape(match[0]);
        return `<span class="highlight-separator">${separator}</span>`;
    }

    let out = $.fn.zato.ide.highlight.replace_tokens(
        text, $.fn.zato.ide.highlight.config.er7_separator_pattern, wrap_match);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One raw ER7 segment line - the segment id, the separators and, for MSH,
// the encoding characters kept as one opaque run.
$.fn.zato.ide.highlight.er7_line_to_html = function(line) {

    let segment_id = line.slice(0, 3);
    let rest = line.slice(3);

    let out = `<span class="highlight-segment">${segment_id}</span>`;

    // MSH-2 is the encoding characters - the very separators the rest of the
    // message uses, so they render as one literal instead of being split
    if(segment_id == "MSH") {

        let second_separator = rest.indexOf("|", 1);

        if(second_separator == -1) {
            second_separator = rest.length;
        }

        let encoding_characters = rest.slice(1, second_separator);
        let escaped = $.fn.zato.ide.highlight.escape(encoding_characters);

        out += '<span class="highlight-separator">|</span>';
        out += `<span class="highlight-encoding">${escaped}</span>`;

        rest = rest.slice(second_separator);
    }

    out += $.fn.zato.ide.highlight.er7_value_to_html(rest);
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// A whole HL7 payload - segment lines get their colors,
// anything else stays escaped plain text.
$.fn.zato.ide.highlight.hl7_to_html = function(text) {

    let html_lines = [];

    for(const line of text.split("\n")) {

        if($.fn.zato.ide.highlight.config.er7_line_pattern.test(line)) {
            html_lines.push($.fn.zato.ide.highlight.er7_line_to_html(line));
        }
        else {
            html_lines.push($.fn.zato.ide.highlight.escape(line));
        }
    }

    let out = html_lines.join("\n");
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// A JSON payload - keys, strings, numbers, keywords and punctuation.
$.fn.zato.ide.highlight.json_to_html = function(text) {

    let wrap_match = function(match) {

        let escape = $.fn.zato.ide.highlight.escape;

        // A string right before a colon is a key ..
        if(match[1]) {

            let string = escape(match[1]);

            if(match[2]) {
                let colon = escape(match[2]);
                return `<span class="highlight-key">${string}</span><span class="highlight-punctuation">${colon}</span>`;
            }

            return `<span class="highlight-string">${string}</span>`;
        }

        // .. numbers and keywords carry no characters that need escaping ..
        if(match[3]) {
            return `<span class="highlight-number">${match[3]}</span>`;
        }

        if(match[4]) {
            return `<span class="highlight-keyword">${match[4]}</span>`;
        }

        // .. and what remains is punctuation.
        let punctuation = escape(match[5]);
        return `<span class="highlight-punctuation">${punctuation}</span>`;
    }

    let out = $.fn.zato.ide.highlight.replace_tokens(
        text, $.fn.zato.ide.highlight.config.json_token_pattern, wrap_match);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// A key=value payload - the key, the equals sign and the value of each line.
$.fn.zato.ide.highlight.key_value_to_html = function(text) {

    let escape = $.fn.zato.ide.highlight.escape;
    let html_lines = [];

    for(const line of text.split("\n")) {

        let separator_index = line.indexOf("=");

        if(separator_index == -1) {
            html_lines.push(escape(line));
            continue;
        }

        let key = escape(line.slice(0, separator_index));
        let value = escape(line.slice(separator_index + 1));

        html_lines.push(`<span class="highlight-key">${key}</span><span class="highlight-punctuation">=</span>${value}`);
    }

    let out = html_lines.join("\n");
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// What format a payload is in when the selector says auto -
// the same decisions the parse endpoint makes.
$.fn.zato.ide.highlight.detect_format = function(data) {

    let stripped = data.trimStart();

    if($.fn.zato.ide.highlight.config.er7_line_pattern.test(stripped)) {
        return "hl7-v2";
    }

    let first_line = data.split("\n", 1)[0];

    if(first_line.includes("=")) {
        return "key-value";
    }

    return "json";
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Whether a payload gets the HL7 treatment - either by the selector's
// explicit choice or by auto detection.
$.fn.zato.ide.highlight.is_hl7 = function(data) {

    let format = $.fn.zato.ide.get_payload_format();

    if(format == "hl7-v2") {
        return true;
    }

    if(format != "auto") {
        return false;
    }

    let detected = $.fn.zato.ide.highlight.detect_format(data);
    return detected == "hl7-v2";
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// The per-format raw highlighters.
$.fn.zato.ide.highlight.renderers = {
    "json": function(data) { return $.fn.zato.ide.highlight.json_to_html(data); },
    "key-value": function(data) { return $.fn.zato.ide.highlight.key_value_to_html(data); },
    "hl7-v2": function(data) { return $.fn.zato.ide.highlight.hl7_to_html(data); },
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

// A payload as highlighted HTML, in whatever format the selector
// or auto detection says it is in.
$.fn.zato.ide.highlight.to_html = function(data) {

    let format = $.fn.zato.ide.get_payload_format();

    if(format == "auto") {
        format = $.fn.zato.ide.highlight.detect_format(data);
    }

    // FHIR payloads are JSON on the wire
    if(format == "fhir") {
        format = "json";
    }

    let renderer = $.fn.zato.ide.highlight.renderers[format];
    let out = renderer(data);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One line of HL7's parsed text as HTML - the header, a segment id
// or a field/component line, each with its own colors.
$.fn.zato.ide.highlight.parsed_line_to_html = function(line) {

    let escape = $.fn.zato.ide.highlight.escape;
    let config = $.fn.zato.ide.highlight.config;

    // The header - the message type with its control id ..
    let header_match = line.match(config.parsed_header_pattern);

    if(header_match) {
        let message_type = escape(header_match[1]);
        let control_id = escape(header_match[2]);
        return `<span class="highlight-segment">${message_type}</span> <span class="highlight-dimmed">(control id ${control_id})</span>`;
    }

    // .. a segment id alone on its line ..
    if(config.parsed_segment_pattern.test(line)) {
        return `<span class="highlight-segment">${line}</span>`;
    }

    // .. a field or component with its reference, label and value ..
    let field_match = line.match(config.parsed_field_pattern);

    if(field_match) {

        let indent = field_match[1];
        let reference = escape(field_match[2]);
        let label = escape(field_match[3]);
        let value = $.fn.zato.ide.highlight.er7_value_to_html(field_match[4]);

        return `${indent}<span class="highlight-reference">${reference}</span>` +
            `  <span class="highlight-label">${label}</span>` +
            `<span class="highlight-punctuation">:</span> ${value}`;
    }

    // .. and anything else, such as blank lines, stays as it is.
    let out = escape(line);
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Renders HL7's parsed text into a pane as highlighted HTML.
$.fn.zato.ide.highlight.render_parsed = function(pane, text) {

    let html_lines = [];

    for(const line of text.split("\n")) {
        html_lines.push($.fn.zato.ide.highlight.parsed_line_to_html(line));
    }

    pane.html(html_lines.join("\n"));
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Repaints one pane's overlay from its textarea and lines their scrolling up.
$.fn.zato.ide.highlight.refresh = function(pane_name) {

    let text_element = $(`#data-${pane_name}`);
    let backdrop = $(`#data-${pane_name}-highlight`);

    let html = $.fn.zato.ide.highlight.to_html(text_element.val());

    // The trailing newline keeps the overlay as tall as the textarea
    // when the payload ends with an empty line
    backdrop.html(html + "\n");

    $.fn.zato.ide.highlight.follow_scroll(pane_name);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// The overlay follows wherever its textarea has scrolled to.
$.fn.zato.ide.highlight.follow_scroll = function(pane_name) {

    let text_element = document.getElementById(`data-${pane_name}`);
    let backdrop = document.getElementById(`data-${pane_name}-highlight`);

    backdrop.scrollTop = text_element.scrollTop;
    backdrop.scrollLeft = text_element.scrollLeft;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Wires one pane up - the wrapper, the overlay behind the textarea
// and the events that keep the two in step.
$.fn.zato.ide.highlight.init_pane = function(pane_name) {

    let text_element = $(`#data-${pane_name}`);

    // The overlay and the textarea share a wrapper so they always align ..
    let wrapper = $("<div>");
    wrapper.addClass("highlight-wrapper");
    text_element.wrap(wrapper);

    // .. the overlay sits behind the transparent text ..
    let backdrop = $("<pre>");
    backdrop.addClass("highlight-backdrop");
    backdrop.attr("id", `data-${pane_name}-highlight`);
    text_element.before(backdrop);

    text_element.addClass("highlight-source");

    // .. typing repaints it ..
    text_element.on("input", function() {
        $.fn.zato.ide.highlight.refresh(pane_name);
    });

    // .. scrolling drags it along ..
    text_element.on("scroll", function() {
        $.fn.zato.ide.highlight.follow_scroll(pane_name);
    });

    // .. and whatever the pane already holds gets its colors right away.
    $.fn.zato.ide.highlight.refresh(pane_name);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Programmatic .val(...) calls repaint the overlay of the pane they touch -
// the browser fires no input event for them.
$.fn.zato.ide.highlight.install_value_hook = function() {

    // jQuery itself may or may not define hooks for textareas,
    // depending on its version
    if($.valHooks.textarea === undefined) {
        $.valHooks.textarea = {};
    }

    $.valHooks.textarea.set = function(element, value) {

        element.value = value;

        for(const pane_name of $.fn.zato.ide.highlight.config.pane_names) {
            if(element.id == `data-${pane_name}`) {
                $.fn.zato.ide.highlight.refresh(pane_name);
            }
        }

        return true;
    };
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$(document).ready(function() {

    for(const pane_name of $.fn.zato.ide.highlight.config.pane_names) {
        $.fn.zato.ide.highlight.init_pane(pane_name);
    }

    $.fn.zato.ide.highlight.install_value_hook();
});

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
