
// Mapper kit - syntax highlighters.
// Two small highlighters, one for JSON and one for expressions, both
// returning HTML for the overlay editor's display layer and for the
// read-only preview panes.

(function($) {

    zato.mapper.highlight = {};

// ////////////////////////////////////////////////////////////////////////

    function escapeHTML(text) {

        var out = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        return out;
    }

    zato.mapper.highlight.escapeHTML = escapeHTML;

// ////////////////////////////////////////////////////////////////////////

    // Highlights JSON text: keys, strings, numbers, keywords and punctuation.
    zato.mapper.highlight.json = function(text) {

        var out = escapeHTML(text);

        // Keys - a quoted string followed by a colon ..
        out = out.replace(
            /(&quot;)((?:[^&]|&(?!quot;))*)(&quot;)(\s*:)/g,
            '<span class="mapper-syntax-key">$1$2$3</span>$4'
        );

        // .. string values ..
        out = out.replace(
            /(:\s*)(&quot;)((?:[^&]|&(?!quot;))*)(&quot;)/g,
            '$1<span class="mapper-syntax-string">$2$3$4</span>'
        );

        // .. numbers ..
        out = out.replace(
            /(:\s*|\[\s*|,\s*)(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)/g,
            '$1<span class="mapper-syntax-number">$2</span>'
        );

        // .. and the literal keywords.
        out = out.replace(
            /(:\s*)(true|false|null)/g,
            '$1<span class="mapper-syntax-keyword">$2</span>'
        );

        return out;
    };

// ////////////////////////////////////////////////////////////////////////

    // Highlights an expression: strings, numbers, functions and operators.
    zato.mapper.highlight.expression = function(text) {

        var out = escapeHTML(text);

        // Strings in either quote style ..
        out = out.replace(
            /(&quot;(?:[^&]|&(?!quot;))*&quot;|'[^']*')/g,
            '<span class="mapper-syntax-string">$1</span>'
        );

        // .. function names starting with a dollar sign ..
        out = out.replace(
            /(\$[A-Za-z]\w*)/g,
            '<span class="mapper-syntax-function">$1</span>'
        );

        // .. numbers ..
        out = out.replace(
            /\b(\d+(?:\.\d+)?)\b/g,
            '<span class="mapper-syntax-number">$1</span>'
        );

        // .. and operators.
        out = out.replace(
            /(:=|!=|&lt;=|&gt;=|[+\-*\/=&amp;])/g,
            '<span class="mapper-syntax-operator">$1</span>'
        );

        return out;
    };

})(jQuery);
