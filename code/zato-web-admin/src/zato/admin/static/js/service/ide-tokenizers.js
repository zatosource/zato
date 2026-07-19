
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// Per-format tokenizers for the invoker panes - each turns raw payload text
// into highlighted HTML, one function per format, plus the shared helpers
// they are all built out of.

$.fn.zato.ide.tokenizers = {};

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.tokenizers.config = {

    // What an ER7 segment line looks like - a three-character segment id
    // followed by the field separator
    "er7_line_pattern": /^[A-Z][A-Z0-9]{2}\|/,

    // The separators of ER7 values - fields, components, repetitions and subcomponents
    "er7_separator_pattern": /[|^~&]/g,

    // The JSON tokens - a string with an optional key colon, a number,
    // a keyword or a piece of punctuation
    "json_token_pattern": /("(?:\\.|[^"\\])*")(\s*:)?|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|\b(true|false|null)\b|([{}\[\],:])/g,

    // The XML tokens - a comment, a CDATA section, a declaration
    // or processing instruction, or a tag
    "xml_token_pattern": /(<!--[\s\S]*?-->)|(<!\[CDATA\[[\s\S]*?\]\]>)|(<[!?][^>]*>)|(<\/?[^>]*>)/g,

    // One XML tag taken apart - the opening bracket, the name,
    // the attributes and the closing bracket
    "xml_tag_pattern": /^(<\/?)([^\s/>]+)([\s\S]*?)(\/?>?)$/,

    // One XML attribute - its name, the equals sign and the quoted value
    "xml_attribute_pattern": /([\w:.-]+)(\s*=\s*)("[^"]*"|'[^']*')/g,

    // How EDIFACT wire text opens - a UNA service string advice
    // or a segment tag followed by the element separator
    "edifact_prefix_pattern": /^(UNA|[A-Z]{3}\+)/,

    // The separators of EDIFACT values - elements, components and the release character
    "edifact_separator_pattern": /[+:?]/g,

    // One EDIFACT segment taken apart - leading whitespace, the tag and the rest
    "edifact_segment_pattern": /^(\s*)([A-Z]{3})([\s\S]*)$/,

    // How many service characters a full UNA advice carries after its tag
    "edifact_una_length": 6,

    // The header line of HL7's pretty text - the message type and its control id
    "pretty_header_pattern": /^(\S+) \(control id (.*)\)$/,

    // A segment id alone on a line of pretty text, EDIFACT repeat counters included
    "pretty_segment_pattern": /^[A-Z][A-Z0-9]{2}(:\S*)?$/,

    // A field or component line of pretty text - indent, reference, label and value
    "pretty_field_pattern": /^(\s+)(\S+)  (.*?): (.*)$/,
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

// The characters that must not reach the overlay as markup.
$.fn.zato.ide.tokenizers.escape = function(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Runs one token pattern over raw text and builds HTML out of it - each token
// goes through the given wrapper and everything in between is escaped plain text.
$.fn.zato.ide.tokenizers.replace_tokens = function(text, pattern, wrap_match) {

    let out = "";
    let last_index = 0;

    // The pattern is shared, so each run starts from the top
    pattern.lastIndex = 0;

    var match;

    while((match = pattern.exec(text)) !== null) {

        let plain = text.slice(last_index, match.index);
        out += $.fn.zato.ide.tokenizers.escape(plain);
        out += wrap_match(match);

        last_index = match.index + match[0].length;
    }

    out += $.fn.zato.ide.tokenizers.escape(text.slice(last_index));
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One ER7 value with its separators colored.
$.fn.zato.ide.tokenizers.er7_value_to_html = function(text) {

    let wrap_match = function(match) {
        let separator = $.fn.zato.ide.tokenizers.escape(match[0]);
        return `<span class="highlight-separator">${separator}</span>`;
    }

    let out = $.fn.zato.ide.tokenizers.replace_tokens(
        text, $.fn.zato.ide.tokenizers.config.er7_separator_pattern, wrap_match);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One raw ER7 segment line - the segment id, the separators and, for MSH,
// the encoding characters kept as one opaque run.
$.fn.zato.ide.tokenizers.er7_line_to_html = function(line) {

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
        let escaped = $.fn.zato.ide.tokenizers.escape(encoding_characters);

        out += '<span class="highlight-separator">|</span>';
        out += `<span class="highlight-encoding">${escaped}</span>`;

        rest = rest.slice(second_separator);
    }

    out += $.fn.zato.ide.tokenizers.er7_value_to_html(rest);
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// A whole HL7 payload - segment lines get their colors,
// anything else stays escaped plain text.
$.fn.zato.ide.tokenizers.hl7_to_html = function(text) {

    let html_lines = [];

    for(const line of text.split("\n")) {

        if($.fn.zato.ide.tokenizers.config.er7_line_pattern.test(line)) {
            html_lines.push($.fn.zato.ide.tokenizers.er7_line_to_html(line));
        }
        else {
            html_lines.push($.fn.zato.ide.tokenizers.escape(line));
        }
    }

    let out = html_lines.join("\n");
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// A JSON payload - keys, strings, numbers, keywords and punctuation.
$.fn.zato.ide.tokenizers.json_to_html = function(text) {

    let wrap_match = function(match) {

        let escape = $.fn.zato.ide.tokenizers.escape;

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

    let out = $.fn.zato.ide.tokenizers.replace_tokens(
        text, $.fn.zato.ide.tokenizers.config.json_token_pattern, wrap_match);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// A key=value payload - the key, the equals sign and the value of each line.
$.fn.zato.ide.tokenizers.key_value_to_html = function(text) {

    let escape = $.fn.zato.ide.tokenizers.escape;
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

// The attributes inside one XML tag - each name, equals sign and quoted value.
$.fn.zato.ide.tokenizers.xml_attributes_to_html = function(text) {

    let wrap_match = function(match) {

        let escape = $.fn.zato.ide.tokenizers.escape;

        let name = escape(match[1]);
        let equals = escape(match[2]);
        let value = escape(match[3]);

        return `<span class="highlight-attribute">${name}</span>` +
            `<span class="highlight-punctuation">${equals}</span>` +
            `<span class="highlight-string">${value}</span>`;
    }

    let out = $.fn.zato.ide.tokenizers.replace_tokens(
        text, $.fn.zato.ide.tokenizers.config.xml_attribute_pattern, wrap_match);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One XML tag - its brackets, name and attributes, each with their own colors.
$.fn.zato.ide.tokenizers.xml_tag_to_html = function(tag_text) {

    let escape = $.fn.zato.ide.tokenizers.escape;
    let match = tag_text.match($.fn.zato.ide.tokenizers.config.xml_tag_pattern);

    // A tag still being typed may not take apart yet
    if(!match) {
        return escape(tag_text);
    }

    let open = escape(match[1]);
    let name = escape(match[2]);
    let body = $.fn.zato.ide.tokenizers.xml_attributes_to_html(match[3]);
    let close = escape(match[4]);

    let out = `<span class="highlight-punctuation">${open}</span>` +
        `<span class="highlight-tag">${name}</span>${body}` +
        `<span class="highlight-punctuation">${close}</span>`;

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// An XML payload - comments, CDATA sections, declarations and tags,
// with the text between them escaped as it is.
$.fn.zato.ide.tokenizers.xml_to_html = function(text) {

    let wrap_match = function(match) {

        let escape = $.fn.zato.ide.tokenizers.escape;

        // A comment ..
        if(match[1]) {
            return `<span class="highlight-comment">${escape(match[1])}</span>`;
        }

        // .. a CDATA section is data, not markup ..
        if(match[2]) {
            return `<span class="highlight-string">${escape(match[2])}</span>`;
        }

        // .. a declaration or processing instruction ..
        if(match[3]) {
            return `<span class="highlight-dimmed">${escape(match[3])}</span>`;
        }

        // .. and what remains is a tag.
        return $.fn.zato.ide.tokenizers.xml_tag_to_html(match[4]);
    }

    let out = $.fn.zato.ide.tokenizers.replace_tokens(
        text, $.fn.zato.ide.tokenizers.config.xml_token_pattern, wrap_match);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One EDIFACT value with its separators colored.
$.fn.zato.ide.tokenizers.edifact_value_to_html = function(text) {

    let wrap_match = function(match) {
        let separator = $.fn.zato.ide.tokenizers.escape(match[0]);
        return `<span class="highlight-separator">${separator}</span>`;
    }

    let out = $.fn.zato.ide.tokenizers.replace_tokens(
        text, $.fn.zato.ide.tokenizers.config.edifact_separator_pattern, wrap_match);

    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One EDIFACT segment - its tag and the separators of everything after it.
$.fn.zato.ide.tokenizers.edifact_segment_to_html = function(segment_text) {

    let match = segment_text.match($.fn.zato.ide.tokenizers.config.edifact_segment_pattern);

    // A part without a tag, such as a fragment still being typed
    if(!match) {
        return $.fn.zato.ide.tokenizers.edifact_value_to_html(segment_text);
    }

    let leading = match[1];
    let tag = match[2];
    let rest = $.fn.zato.ide.tokenizers.edifact_value_to_html(match[3]);

    let out = `${leading}<span class="highlight-segment">${tag}</span>${rest}`;
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// An EDIFACT payload - the UNA advice as one opaque run, then each segment
// with its tag and separators colored.
$.fn.zato.ide.tokenizers.edifact_to_html = function(text) {

    let out = "";
    let rest = text;

    // The UNA advice carries the very separators everything else uses,
    // so its service characters render as one literal
    if(rest.startsWith("UNA")) {

        let una_end = 3 + $.fn.zato.ide.tokenizers.config.edifact_una_length;
        let service_characters = $.fn.zato.ide.tokenizers.escape(rest.slice(3, una_end));

        out += '<span class="highlight-segment">UNA</span>';
        out += `<span class="highlight-encoding">${service_characters}</span>`;

        rest = rest.slice(una_end);
    }

    // Each terminator concludes a segment and the tag right after it gets its color
    let html_parts = [];

    for(const part of rest.split("'")) {
        html_parts.push($.fn.zato.ide.tokenizers.edifact_segment_to_html(part));
    }

    out += html_parts.join('<span class="highlight-separator">\'</span>');
    return out;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// One line of pretty text as HTML - the header, a segment id or a field line,
// with the given value colorer applied to field values.
$.fn.zato.ide.tokenizers.pretty_line_to_html = function(line, value_to_html) {

    let escape = $.fn.zato.ide.tokenizers.escape;
    let config = $.fn.zato.ide.tokenizers.config;

    // The header - the message type with its control id ..
    let header_match = line.match(config.pretty_header_pattern);

    if(header_match) {
        let message_type = escape(header_match[1]);
        let control_id = escape(header_match[2]);
        return `<span class="highlight-segment">${message_type}</span> <span class="highlight-dimmed">(control id ${control_id})</span>`;
    }

    // .. a segment id alone on its line ..
    if(config.pretty_segment_pattern.test(line)) {
        return `<span class="highlight-segment">${escape(line)}</span>`;
    }

    // .. a field or component with its reference, label and value ..
    let field_match = line.match(config.pretty_field_pattern);

    if(field_match) {

        let indent = field_match[1];
        let reference = escape(field_match[2]);
        let label = escape(field_match[3]);
        let value = value_to_html(field_match[4]);

        return `${indent}<span class="highlight-reference">${reference}</span>` +
            `  <span class="highlight-label">${label}</span>` +
            `<span class="highlight-punctuation">:</span> ${value}`;
    }

    // .. and anything else, such as blank lines, stays as it is.
    let out = escape(line);
    return out;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
