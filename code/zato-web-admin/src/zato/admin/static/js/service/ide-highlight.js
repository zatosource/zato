
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Syntax highlighting for the invoker panes - the raw textareas get a colored
// overlay behind their transparent text and the pretty view of a payload gets
// its colored HTML built by the per-format tokenizers from ide-tokenizers.js.

$.fn.zato.ide.highlight = {};

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.highlight.config = {

    // Which panes carry a highlighted overlay
    "pane_names": ["request", "response"],

    // The formats whose payloads have a pretty view
    "pretty_formats": ["hl7-v2", "xml", "edifact"],
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

// What format a payload is in when the selector says auto -
// the same decisions the parse endpoint makes.
$.fn.zato.ide.highlight.detect_format = function(data) {

    let tokenizers = $.fn.zato.ide.tokenizers;
    let stripped = data.trimStart();

    if(tokenizers.config.er7_line_pattern.test(stripped)) {
        return "hl7-v2";
    }

    if(stripped.startsWith("<")) {
        return "xml";
    }

    if(tokenizers.config.edifact_prefix_pattern.test(stripped)) {
        return "edifact";
    }

    let first_line = data.split("\n", 1)[0];

    if(first_line.includes("=")) {
        return "key-value";
    }

    return "json";
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// The format a payload gets treated as - the selector's explicit choice,
// with auto detection filling in for the auto one.
$.fn.zato.ide.highlight.resolve_format = function(data) {

    let format = $.fn.zato.ide.get_payload_format();

    if(format == "auto") {
        format = $.fn.zato.ide.highlight.detect_format(data);
    }

    return format;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Whether a payload has a pretty view - only the formats
// with a textual tree rendering do.
$.fn.zato.ide.highlight.has_pretty_view = function(data) {

    let format = $.fn.zato.ide.highlight.resolve_format(data);

    let out = $.fn.zato.ide.highlight.config.pretty_formats.includes(format);
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// The per-format raw highlighters.
$.fn.zato.ide.highlight.renderers = {
    "json": function(data) { return $.fn.zato.ide.tokenizers.json_to_html(data); },
    "key-value": function(data) { return $.fn.zato.ide.tokenizers.key_value_to_html(data); },
    "hl7-v2": function(data) { return $.fn.zato.ide.tokenizers.hl7_to_html(data); },
    "xml": function(data) { return $.fn.zato.ide.tokenizers.xml_to_html(data); },
    "edifact": function(data) { return $.fn.zato.ide.tokenizers.edifact_to_html(data); },
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

// A payload as highlighted HTML, in whatever format the selector
// or auto detection says it is in.
$.fn.zato.ide.highlight.to_html = function(data) {

    let format = $.fn.zato.ide.highlight.resolve_format(data);

    // FHIR payloads are JSON on the wire
    if(format == "fhir") {
        format = "json";
    }

    let renderer = $.fn.zato.ide.highlight.renderers[format];
    let out = renderer(data);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Renders a payload's pretty text into a pane as highlighted HTML - the raw
// payload decides the format, since the pretty text itself no longer shows it.
$.fn.zato.ide.highlight.render_pretty = function(pane, text, data) {

    let tokenizers = $.fn.zato.ide.tokenizers;
    let format = $.fn.zato.ide.highlight.resolve_format(data);

    // Pretty XML is still XML, so its own tokenizer colors it whole ..
    if(format == "xml") {
        pane.html(tokenizers.xml_to_html(text));
        return;
    }

    // .. while the segment formats color their indented tree line by line,
    // each with the value colorer of its own wire syntax.
    if(format == "edifact") {
        var value_to_html = function(value) { return tokenizers.edifact_value_to_html(value); };
    }
    else {
        var value_to_html = function(value) { return tokenizers.er7_value_to_html(value); };
    }

    let html_lines = [];

    for(const line of text.split("\n")) {
        html_lines.push(tokenizers.pretty_line_to_html(line, value_to_html));
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
