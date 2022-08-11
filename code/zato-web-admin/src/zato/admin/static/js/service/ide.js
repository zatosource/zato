
$.fn.zato.editor.init_editor = function() {
    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/sqlserver");
    editor.session.setMode("ace/mode/python");

    editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        newLineMode: "unix",
        fontSize: 17,
        cursorStyle: "ace"
    });
    $.fn.zato.editor.populate_browser_area();
}

$.fn.zato.editor.toggle_action_area = function() {

    let css_property = "grid-template-columns";
    // let default_size = "3.9fr 1fr 0.06fr";
    // let expanded_size = "1.0fr 1fr 0.06fr";

    let default_size = "1.0fr 1fr 0.06fr";
    let expanded_size = "3.9fr 1fr 0.06fr";

    let main_area_container = $("#main-area-container");
    let elem_to_expand = $("#action-area-header");

    let is_expanded = elem_to_expand.attr("data-is-expanded");

    if(is_expanded == "false") {
        new_size = expanded_size;
        elem_to_expand.attr("data-is-expanded", "true");
    }
    else {
        new_size = default_size
        elem_to_expand.attr("data-is-expanded", "false");
    }

    main_area_container.css(css_property, new_size);
}

$.fn.zato.editor.switch_to_action_area = function(name) {
    console.log("Name -> " + name);
    if(name == "browser") {
        $.fn.zato.editor.populate_browser_area();
    }
    else if(name == "invoker") {
        $.fn.zato.editor.populate_invoker_area();
    }
    else if(name == "info") {
        $.fn.zato.editor.populate_data_model_area();
    }
}

$.fn.zato.editor.clear_header_links = function(prefix) {

    // The element where all the links reside ..
    let header_links_id = `#header-links-${prefix}`;
    let header_links = $(header_links_id);

    // .. clean it up.
    header_links.empty();
}

$.fn.zato.editor.add_header_link = function(prefix, item_no, text, is_last) {

    // The element where all the links reside ..
    let header_links_id = `#header-links-${prefix}`;
    let header_links = $(header_links_id);

    // .. this is what each link will be based on ..
    let link_pattern = '<a href="$.fn.zato.editor.invoke_header_link(\"{0}\", {1})" id="header-{0}-link-{1}">{2}</a>';

    // .. build a string containing the link ..
    let link_string = String.format(link_pattern, prefix, item_no, text);

    // .. now, the element ..
    link = $(link_string);

    // .. now, append it to our links ..
    header_links.append(link);

    // .. and add a separator unless this is the last link.
    if(!is_last) {
        $("<span> | </span>").insertAfter(link);
    }
}

$.fn.zato.editor.add_header_left_link = function(item_no, text, is_last) {
    $.fn.zato.editor.add_header_link("left", item_no, text, is_last);
}

$.fn.zato.editor.add_header_right_link = function(item_no, text, is_last) {
    $.fn.zato.editor.add_header_link("right", item_no, text, is_last);
}

$.fn.zato.editor.populate_header_status = function(text) {
    let elem_id = `#header-status`;
    let elem = $(elem_id);
    elem.text(text);
}

$.fn.zato.editor.populate_browser_area = function() {

    // Clear anything that we may already have
    $.fn.zato.editor.clear_header_links("left")
    $.fn.zato.editor.clear_header_links("right")

    // Make sure that we are only showing our own area now
    $('.file-listing-tr').show();
    $('.invoker-tr').hide();

    // Left-hand side links
    $.fn.zato.editor.add_header_left_link(1, "Deploy");
    $.fn.zato.editor.add_header_left_link(2, "Deploy all");
    $.fn.zato.editor.add_header_left_link(3, "New", true);

    // Right-hand side links
    $.fn.zato.editor.add_header_right_link(1, "Push", true);

    // One-line status bar
    $("#header-status").text("4 files, 9 services");
}

$.fn.zato.editor.populate_invoker_area = function() {

    // Clear anything that we may already have
    $.fn.zato.editor.clear_header_links("left")
    $.fn.zato.editor.clear_header_links("right")

    // Make sure that we are only showing our own area now
    $('.file-listing-tr').hide();
    $('.invoker-tr').show();

    // Left-hand side links
    $.fn.zato.editor.add_header_left_link(1, "Deploy");
    $.fn.zato.editor.add_header_left_link(2, "Deploy all");
    $.fn.zato.editor.add_header_left_link(3, "Previous");
    $.fn.zato.editor.add_header_left_link(4, "Next");
    $.fn.zato.editor.add_header_left_link(5, "Clear form", true);

    // Right-hand side links
    $.fn.zato.editor.add_header_right_link(1, "OpenAPI", true);

    // One-line status bar
    $("#header-status").text("curl http://api:api@10.151.19.39:11223/zato/api/api.adapter.crm.customer.create -d '{\"customer_id\":\"123\"}'");
    /*
    $("#header-status").text("curl http://api:api@10.151.19.39:11223/zato/api/api.adapter.crm.customer.create -d '{\"customer_id\":\"123\"}'");
    $("<a href=\"#\">Edit</a>").insertAfter("#header-status");
    $("<a class=\"header-sublink-first\" href=\"#\">Copy</a>").insertAfter("#header-status");
    */
}

$.fn.zato.editor.populate_data_model_area = function() {
}
