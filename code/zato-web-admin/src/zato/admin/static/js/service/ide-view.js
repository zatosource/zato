
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

// View switching for the invoker panes - each pane offers its payload as the tree,
// pretty or raw view, remembers the choice per service and keeps its view links
// in step with whatever is pasted or typed into it.

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_pane_view_key = function(pane_name) {
    let service_name = $.fn.zato.ide.get_current_service_name();
    return $.fn.zato.ide.config.pane_view_key_prefix + pane_name + "." + service_name;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Keeps a pane's view links in step with its payload - the pretty link exists
// only for the formats that have a textual rendering, so it comes and goes
// as the content changes. Returns whether the payload has a pretty view.
$.fn.zato.ide.refresh_view_links = function(pane_name) {

    let text_elem = pane_name == "request" ? $("#data-request") : $("#data-response");
    let data = text_elem.val();

    let has_pretty = $.fn.zato.ide.highlight.has_pretty_view(data);

    $(`#${pane_name}-view-pretty`).toggleClass("hidden", !has_pretty);
    $(`#${pane_name}-view-pretty-separator`).toggleClass("hidden", !has_pretty);

    return has_pretty;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.apply_pane_view = function(pane_name) {

    // The remembered choice for this pane and service ..
    let key = $.fn.zato.ide.get_pane_view_key(pane_name);
    var view_name = localStorage.getItem(key);

    // .. a pane seen for the first time starts with the default ..
    if(view_name === null) {
        view_name = $.fn.zato.ide.config.default_pane_view;
    }

    // .. a choice remembered under the view's earlier name still counts ..
    if(view_name == "parsed") {
        view_name = "pretty";
    }

    // .. and re-applying a remembered view is not a new choice to persist.
    $.fn.zato.ide.show_pane_view(pane_name, view_name, false);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.show_pane_view = function(pane_name, view_name, should_persist) {

    let text_elem = pane_name == "request" ? $("#data-request") : $("#data-response");
    let pretty_elem = $(`#data-${pane_name}-pretty`);

    let tree_link = $(`#${pane_name}-view-tree`);
    let raw_link = $(`#${pane_name}-view-raw`);
    let pretty_link = $(`#${pane_name}-view-pretty`);

    let data = text_elem.val();

    // The links always reflect what the payload offers
    let has_pretty = $.fn.zato.ide.refresh_view_links(pane_name);

    // An empty pane has nothing to parse, so it shows as raw without
    // overwriting whatever view is remembered ..
    if(!data) {
        view_name = "raw";
        should_persist = false;
    }

    // .. and a remembered pretty view of a payload without one shows as the tree.
    if(view_name == "pretty") {
        if(!has_pretty) {
            view_name = "tree";
        }
    }

    // A view chosen by hand is remembered for this pane and service
    if(should_persist !== false) {
        let service_name = $.fn.zato.ide.get_current_service_name();
        if(service_name) {
            localStorage.setItem($.fn.zato.ide.get_pane_view_key(pane_name), view_name);
        }
    }

    // The drag-to-resize indicator belongs to the raw request view only
    let resize_indicator = $("#data-request-resize-indicator");

    // Only one link reads as the current one
    let mark_current = function(link) {
        tree_link.removeClass("current");
        raw_link.removeClass("current");
        pretty_link.removeClass("current");
        link.addClass("current");
    }

    if(view_name == "raw") {
        pretty_elem.addClass("hidden");
        text_elem.removeClass("hidden");
        mark_current(raw_link);

        // The overlay repaints in case the payload changed while another view was up
        $.fn.zato.ide.highlight.refresh(pane_name);

        if(pane_name == "request") {
            resize_indicator.removeClass("hidden");
        }
        return;
    }

    // The rendered views take over the exact height of the raw one,
    // so the swap never moves anything below the pane
    if(pane_name == "request") {
        let raw_height = text_elem[0].style.height;
        if(raw_height) {
            pretty_elem.css("height", raw_height);
        }
    }

    // Brings the rendered pane forward once it has its content
    let show_rendered_pane = function(link) {
        text_elem.addClass("hidden");
        pretty_elem.removeClass("hidden");
        mark_current(link);

        if(pane_name == "request") {
            resize_indicator.addClass("hidden");
        }
    }

    // Both remaining views get their content from the parse endpoint,
    // except for the tree of a JSON payload
    let fetch_views = function(handler) {
        let format = $.fn.zato.ide.get_payload_format();
        $.ajax({
            type: "POST",
            url: $.fn.zato.ide.config.parse_payload_url,
            data: JSON.stringify({"data": data, "data_format": format}),
            contentType: "application/json",
            headers: {"X-CSRFToken": $.cookie("csrftoken")},
            success: handler
        });
    }

    if(view_name == "tree") {

        // A payload that parses as JSON becomes the grid view,
        // built right here without a round trip ..
        try {
            var parsed_json = JSON.parse(data);
            var is_json = true;
        }
        catch(ignored) {
            var is_json = false;
        }

        if(is_json) {
            $.fn.zato.ide.render_grid_view(pretty_elem, parsed_json);
            show_rendered_pane(tree_link);
            return;
        }

        // .. every other format gets its grid nodes from the parse endpoint.
        fetch_views(function(response) {

            let nodes = response.tree;

            if(nodes.length) {

                let root = $("<div>").addClass("grid-view");

                for(const node of nodes) {
                    root.append($.fn.zato.ide.build_grid_view_node(node, ""));
                }

                pretty_elem.empty();
                pretty_elem.append(root);
            }
            else {
                pretty_elem.text($.fn.zato.ide.config.parse_failed_text);
            }

            show_rendered_pane(tree_link);
        });
        return;
    }

    // What is left is the pretty view - the payload's textual rendering, highlighted.
    fetch_views(function(response) {

        let pretty_text = response.pretty_text;

        if(pretty_text === "") {
            pretty_elem.text($.fn.zato.ide.config.parse_failed_text);
        }
        else {
            $.fn.zato.ide.highlight.render_pretty(pretty_elem, pretty_text, data);
        }

        show_rendered_pane(pretty_link);
    });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.update_view_toggles = function() {

    let format = $.fn.zato.ide.get_payload_format();

    // The remembered view of each pane is re-applied under the new format
    $.fn.zato.ide.apply_pane_view("request");
    $.fn.zato.ide.apply_pane_view("response");

    // Samples exist only for some formats
    let sample_list = $.fn.zato.ide.config.samples[format];

    if(sample_list === undefined) {
        $("#insert-sample-link").addClass("hidden");
    }
    else {
        $("#insert-sample-link").removeClass("hidden");
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$(document).ready(function() {

    // Pasting or typing into a pane updates its view links right away,
    // so a freshly pasted message can go straight to its tree or pretty view
    for(const pane_name of $.fn.zato.ide.highlight.config.pane_names) {
        $(`#data-${pane_name}`).on("input", function() {
            $.fn.zato.ide.refresh_view_links(pane_name);
        });
    }
});

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
