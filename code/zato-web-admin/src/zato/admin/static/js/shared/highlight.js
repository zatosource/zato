// The shared syntax highlighting machinery - a textarea keeps its own text
// transparent and a colored copy of it is painted on an overlay right behind the
// caret, which is how a plain textarea comes to look highlighted. The tokenizers
// that turn text into that colored copy are per format, the two below are the
// plumbing every one of them is built on, and the ini one is here because config
// files are read on more than one page. The look lives in shared/highlight.css.

(function($) {

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.highlight = {};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.highlight.config = {

    // How an ini file's lines open - a comment, a section header of any depth,
    // and a section header taken apart into its brackets and its name
    comment_pattern: /^\s*[#;]/,
    section_pattern: /^\s*\[+[^\]]*\]+\s*$/,
    section_parts_pattern: /^(\s*)(\[+)([^\]]*)(\]+)(\s*)$/,

    // A comment that follows a value on the same line
    inline_comment_pattern: /\s[#;]/,

    // A value that is a number rather than a word
    number_pattern: /^-?\d+(?:\.\d+)?$/,

    // What separates a key from its value
    key_separator: '=',

    // The block keywords of a rules file, each alone on an unindented line
    rules_keyword_pattern: /^(rule|docs|defaults|when|then|else)$/,

    // The values inside a rule's lines - a string or datetime literal, a number
    // standing on its own, and the words the rules language reads as keywords
    rules_token_pattern: /(d?'(?:\\.|[^'\\])*')|(?<![\w'.-])(-?\d+(?:\.\d+)?)(?![\w'])|\b(true|false|and|or)\b/g,

    // What an assignment's target is set apart from its value by
    rules_assignment_separator: ' = '
};

// ////////////////////////////////////////////////////////////////////////

// The characters that must not reach the overlay as markup.
$.fn.zato.highlight.escape = function(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
};

// ////////////////////////////////////////////////////////////////////////

// Runs one token pattern over raw text and builds HTML out of it - each token
// goes through the given wrapper and everything in between is escaped plain text.
$.fn.zato.highlight.replace_tokens = function(text, pattern, wrap_match) {

    var out = '';
    var last_index = 0;

    // The pattern is shared, so each run starts from the top
    pattern.lastIndex = 0;

    var match;

    while((match = pattern.exec(text)) !== null) {

        var plain = text.slice(last_index, match.index);

        out += $.fn.zato.highlight.escape(plain);
        out += wrap_match(match);

        last_index = match.index + match[0].length;
    }

    out += $.fn.zato.highlight.escape(text.slice(last_index));
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One span of colored text.
$.fn.zato.highlight.wrap = function(className, text) {

    var escaped = $.fn.zato.highlight.escape(text);
    var out = '<span class="' + className + '">' + escaped + '</span>';

    return out;
};

// ////////////////////////////////////////////////////////////////////////
// The ini format
// ////////////////////////////////////////////////////////////////////////

// A whole ini file - each line is a comment, a section header, a key with its
// value, or something that belongs to none of those and stays plain.
$.fn.zato.highlight.ini_to_html = function(text) {

    var html_lines = [];
    var lineList = text.split('\n');

    for(var lineIdx = 0; lineIdx < lineList.length; lineIdx++) {
        html_lines.push($.fn.zato.highlight.ini_line_to_html(lineList[lineIdx]));
    }

    var out = html_lines.join('\n');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.highlight.ini_line_to_html = function(line) {

    var highlight = $.fn.zato.highlight;
    var config = highlight.config;

    if(config.comment_pattern.test(line)) {
        return highlight.wrap('highlight-comment', line);
    }

    if(config.section_pattern.test(line)) {
        return highlight.ini_section_to_html(line);
    }

    var separatorIdx = line.indexOf(config.key_separator);

    if(separatorIdx === -1) {
        return highlight.escape(line);
    }

    var key = line.slice(0, separatorIdx);
    var value = line.slice(separatorIdx + 1);

    var out = highlight.wrap('highlight-key', key) +
        highlight.wrap('highlight-punctuation', config.key_separator) +
        highlight.ini_value_to_html(value);

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// A section header of any depth - the brackets are what say how deeply nested
// the section is, so they are colored apart from the name they hold.
$.fn.zato.highlight.ini_section_to_html = function(line) {

    var highlight = $.fn.zato.highlight;
    var parts = highlight.config.section_parts_pattern.exec(line);

    var out = parts[1] +
        highlight.wrap('highlight-punctuation', parts[2]) +
        highlight.wrap('highlight-section', parts[3]) +
        highlight.wrap('highlight-punctuation', parts[4]) +
        parts[5];

    return out;
};

// ////////////////////////////////////////////////////////////////////////

// What a key is set to - a number reads as one, anything else as text, a comment
// after it reads as a comment, and the space around it all stays where it is.
$.fn.zato.highlight.ini_value_to_html = function(value) {

    var highlight = $.fn.zato.highlight;
    var comment = '';

    var commentIdx = value.search(highlight.config.inline_comment_pattern);

    if(commentIdx !== -1) {
        comment = highlight.wrap('highlight-comment', value.slice(commentIdx));
        value = value.slice(0, commentIdx);
    }

    var trimmed = value.trim();

    if(!trimmed) {
        return highlight.escape(value) + comment;
    }

    var className = 'highlight-string';

    if(highlight.config.number_pattern.test(trimmed)) {
        className = 'highlight-number';
    }

    var openingIdx = value.indexOf(trimmed);
    var leading = value.slice(0, openingIdx);
    var trailing = value.slice(openingIdx + trimmed.length);

    var out = leading + highlight.wrap(className, trimmed) + trailing + comment;
    return out;
};

// ////////////////////////////////////////////////////////////////////////
// The rules format
// ////////////////////////////////////////////////////////////////////////

// A whole rules file - the canonical text the rule engine renders. Each line is
// a block keyword, the rule's name, a docs line, an assignment or a condition,
// and which one it is follows from the block the line stands under.
$.fn.zato.highlight.rules_to_html = function(text) {

    var highlight = $.fn.zato.highlight;
    var html_lines = [];
    var block = '';

    var lineList = text.split('\n');

    for(var lineIdx = 0; lineIdx < lineList.length; lineIdx++) {

        var line = lineList[lineIdx];

        // A block keyword opens a new block and is a line of its own
        if(highlight.config.rules_keyword_pattern.test(line)) {
            block = line;
            html_lines.push(highlight.wrap('highlight-keyword', line));
            continue;
        }

        html_lines.push(highlight.rules_line_to_html(line, block));
    }

    var out = html_lines.join('\n');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

$.fn.zato.highlight.rules_line_to_html = function(line, block) {

    var highlight = $.fn.zato.highlight;

    // The line under the rule keyword is the rule's own name
    if(block === 'rule') {
        return highlight.wrap('highlight-section', line);
    }

    // Docs are prose and read the way comments do
    if(block === 'docs') {
        return highlight.wrap('highlight-comment', line);
    }

    // An assignment names its target apart from the value it sets
    var separator = highlight.config.rules_assignment_separator;
    var separatorIdx = line.indexOf(separator);

    if(block !== 'when' && separatorIdx !== -1) {

        var key = line.slice(0, separatorIdx);
        var value = line.slice(separatorIdx + separator.length);

        var out = highlight.wrap('highlight-key', key) +
            highlight.wrap('highlight-punctuation', separator) +
            highlight.rules_value_to_html(value);

        return out;
    }

    // A condition keeps its subject and comparator plain and colors only its values
    return highlight.rules_value_to_html(line);
};

// ////////////////////////////////////////////////////////////////////////

// The literals of one line - strings, numbers and the words that read as keywords.
$.fn.zato.highlight.rules_value_to_html = function(text) {

    var highlight = $.fn.zato.highlight;

    var wrap_match = function(match) {

        if(match[1]) {
            return highlight.wrap('highlight-string', match[1]);
        }

        if(match[2]) {
            return highlight.wrap('highlight-number', match[2]);
        }

        return highlight.wrap('highlight-keyword', match[3]);
    };

    var out = highlight.replace_tokens(text, highlight.config.rules_token_pattern, wrap_match);
    return out;
};

// ////////////////////////////////////////////////////////////////////////
// The overlay
// ////////////////////////////////////////////////////////////////////////

// Puts the overlay behind one textarea and keeps the two in step - typing
// repaints it and scrolling drags it along. The tokenizer is whichever format
// the textarea holds.
//
// The colored copy is held in a box of its own inside the overlay and that box is
// moved, rather than the overlay being scrolled. A textarea with a long line in it
// keeps a scrollbar along its foot and so has more room to scroll than the overlay
// behind it does, and an overlay that was scrolled would stop short of the last lines
// of such a file while the textarea went on.
$.fn.zato.highlight.attach = function(textarea, to_html) {

    var wrapper = document.createElement('div');
    wrapper.className = 'highlight-wrapper';

    var backdrop = document.createElement('pre');
    backdrop.className = 'highlight-backdrop';

    var text = document.createElement('div');
    text.className = 'highlight-backdrop-text';

    backdrop.appendChild(text);

    textarea.parentNode.insertBefore(wrapper, textarea);
    wrapper.appendChild(backdrop);
    wrapper.appendChild(textarea);

    textarea.classList.add('highlight-source');

    // The tokenizer stays with the textarea, so a repaint asked for from
    // anywhere else needs nothing but the textarea itself
    textarea.zato_to_html = to_html;

    textarea.addEventListener('input', function() {
        $.fn.zato.highlight.refresh(textarea);
    });

    textarea.addEventListener('scroll', function() {
        $.fn.zato.highlight.follow_scroll(textarea);
    });

    $.fn.zato.highlight.refresh(textarea);
};

// ////////////////////////////////////////////////////////////////////////

// Repaints one textarea's overlay from what the textarea now holds - anything
// that sets its value from code calls this, since no input event is fired for it.
$.fn.zato.highlight.refresh = function(textarea) {

    var text = $.fn.zato.highlight.get_text(textarea);
    var html = textarea.zato_to_html(textarea.value);

    // The trailing newline keeps the overlay as tall as the textarea when the
    // text ends with an empty line
    text.innerHTML = html + '\n';

    $.fn.zato.highlight.follow_scroll(textarea);
};

// ////////////////////////////////////////////////////////////////////////

// The overlay follows wherever its textarea has scrolled to.
$.fn.zato.highlight.follow_scroll = function(textarea) {

    var text = $.fn.zato.highlight.get_text(textarea);
    var left = -textarea.scrollLeft;
    var top = -textarea.scrollTop;

    text.style.transform = 'translate(' + left + 'px, ' + top + 'px)';
};

// ////////////////////////////////////////////////////////////////////////

// The box the colored copy is held in, which is the one thing in the overlay that moves.
$.fn.zato.highlight.get_text = function(textarea) {

    var out = textarea.previousElementSibling.firstElementChild;
    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
