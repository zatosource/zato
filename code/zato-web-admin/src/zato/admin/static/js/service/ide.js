
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$(document).ready(function() {
    $('#invoke-service').click($.fn.zato.invoker.on_invoke_submitted);
    $('#header-left-link-deploy').click($.fn.zato.invoker.on_deploy_submitted);
});

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.init_editor = function(initial_header_status) {

    // All the keys that we use with LocalStorage
    window.zato_local_storage_key = {
        'zato_action_area_size': 'zato.action-area-size',
    }

    // Our initial file that we process
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();

    // Maps file names to Ace EditorSession objects.
    window.zato_editor_session_map = {};

    window.zato_editor = ace.edit("editor");
    window.zato_editor.setTheme("ace/theme/zato");
    $.fn.zato.ide.set_up_editor_session(window.zato_editor.session);

    window.zato_editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        newLineMode: "unix",
        fontSize: 16,
        fontFamily: "Ubuntu Mono",
        cursorStyle: "ace"
    });

    // Store a reference to the editor as we will be likely switching to various files
    window.zato_editor_session_map[current_fs_location] = window.zato_editor;

    // Set initial data
    $.fn.zato.ide.populate_invoker_area();

    // Handle browser history back/forward actions
    window.onpopstate = function(event) {
        let name = event.state.name;
        $.fn.zato.ide.populate_document_title(name);
    }

    // Resizes the action area
    hotkeys('F2', $.fn.zato.ide.on_key_f2);

    // Same as above (F2)
    window.zato_editor.commands.addCommand({
        name: 'on_F2',
        bindKey: {win: 'F2',  mac: 'F2'},
        exec: function(_ignored_editor) {
            $.fn.zato.ide.on_key_f2(null, null);
        }
    })

    window.zato_inactivity_interval = null;
    document.onkeydown = $.fn.zato.ide.reset_inactivity_timeout;

    // This will try to load all the remember layout options from LocalStorage
    $.fn.zato.ide.restore_layout();

    // This will try to load the content from LocalStorage
    $.fn.zato.ide.load_current_source_code_from_local_storage();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.reset_inactivity_timeout = function() {
    clearTimeout(window.zato_inactivity_interval);
    $.fn.zato.ide.set_inactivity_handler();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_inactivity_handler = function() {
    window.zato_inactivity_interval = setTimeout($.fn.zato.ide.handle_inactivity, 200)
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.handle_inactivity = function() {
    $.fn.zato.ide.save_current_source_code_to_local_storage();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.save_current_source_code_to_local_storage = function() {
    let key = $.fn.zato.ide.get_current_source_code_key()
    let value = window.zato_editor.getValue();
    store.set(key, value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_current_source_code_from_local_storage = function() {
    let key = $.fn.zato.ide.get_current_source_code_key()
    let value = store.get(key)
    if(value) {
        window.zato_editor.setValue(value);
        window.zato_editor.clearSelection();
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.restore_layout = function() {
    let size = store.get(window.zato_local_storage_key.zato_action_area_size);
    if(size) {
        $.fn.zato.ide.set_main_area_container_size(size);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Resizes the action area
$.fn.zato.ide.on_key_f2 = function(_ignored_event, _ignored_handler) {
    $.fn.zato.ide.toggle_action_area();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.toggle_action_area = function() {

    // let default_size = "3.9fr 1fr 0.06fr";
    // let expanded_size = "1.0fr 1fr 0.06fr";

    let service_select = $("#service-select");

    let default_size = "1.0fr 1fr 0.06fr";
    let expanded_size = "3.9fr 1fr 0.06fr";

    let elem_to_expand = $("#action-area-header");
    let is_expanded = elem_to_expand.attr("data-is-expanded");

    if(is_expanded == "false") {
        new_size = expanded_size;
        elem_to_expand.attr("data-is-expanded", "true");
        $.fn.zato.toggle_css_class(service_select, "expanded", "default");
    }
    else {
        new_size = default_size
        elem_to_expand.attr("data-is-expanded", "false");
        $.fn.zato.toggle_css_class(service_select, "default", "expanded");
    }

    // Set the current layout ..
    $.fn.zato.ide.set_main_area_container_size(new_size);

    // .. and persist it for later use.
    store.set(window.zato_local_storage_key.zato_action_area_size, new_size);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_main_area_container_size = function(size) {
    let main_area_container = $("#main-area-container");
    let css_property = "grid-template-columns";
    main_area_container.css(css_property, size);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.switch_to_action_area = function(name) {

    if(name == "invoker") {
        $.fn.zato.ide.populate_invoker_area();
    }
    else if(name == "info") {
        $.fn.zato.ide.populate_data_model_area();
    }
    else if(name == "settings") {
        $.fn.zato.ide.populate_settings_area();
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.clear_header_links = function(prefix) {

    // The element where all the links reside ..
    let header_links_id = `#header-links-${prefix}`;
    let header_links = $(header_links_id);

    // .. clean it up.
    header_links.empty();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.add_header_link = function(prefix, item_label, text, is_last) {

    // The element where all the links reside ..
    let header_links_id = `#header-links-${prefix}`;
    let header_links = $(header_links_id);

    // .. this is what each link will be based on ..
    let link_pattern = '<input type="button" id="header-{0}-link-{1}" value="{2}"></button>';

    // .. build a string containing the link ..
    let link_string = String.format(link_pattern, prefix, item_label, text);

    // .. now, the element ..
    link = $(link_string);

    // .. now, append it to our links ..
    header_links.append(link);

    // .. and add a separator unless this is the last link.
    if(!is_last) {
        $("<span> </span>").insertAfter(link);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.add_header_left_link = function(item_label, text, is_last) {
    $.fn.zato.ide.add_header_link("left", item_label, text, is_last);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.add_header_right_link = function(item_label, text, is_last) {
    $.fn.zato.ide.add_header_link("right", item_label, text, is_last);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_header_status = function(text) {
    let elem_id = `#header-status`;
    let elem = $(elem_id);
    elem.text(text);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_invoker_area = function(initial_header_status) {

    // Clear anything that we may already have
    $.fn.zato.ide.clear_header_links("left")
    $.fn.zato.ide.clear_header_links("right")

    // Make sure that we are only showing our own area now
    $('.file-listing-tr').hide();
    $('.invoker-tr').show();

    // Left-hand side links
    $.fn.zato.ide.add_header_left_link("deploy", "Deploy");
    $.fn.zato.ide.add_header_left_link("file", "File");
    // $.fn.zato.ide.add_header_left_link("deploy-all-changed", "Deploy all changed");
    $.fn.zato.ide.add_header_left_link("previous", "Previous");
    $.fn.zato.ide.add_header_left_link("next", "Next", true);
    // $.fn.zato.ide.add_header_left_link("clear-request", "Clear request", true);

    // Right-hand side links
    //$.fn.zato.ide.add_header_right_link("open-api", "OpenAPI", true);
    $.fn.zato.ide.add_header_right_link("push", "Push");
    $.fn.zato.ide.add_header_right_link("push-all", "Push all", true);

    // One-line status bar
    // $("#header-status").text("curl http://api:api@10.151.19.39:11223/zato/api/api.adapter.crm.customer.create -d '{\"customer_id\":\"123\"}'");
    /*
    $("#header-status").text("curl http://api:api@10.151.19.39:11223/zato/api/api.adapter.crm.customer.create -d '{\"customer_id\":\"123\"}'");
    $("<a href=\"#\">Edit</a>").insertAfter("#header-status");
    $("<a class=\"header-sublink-first\" href=\"#\">Copy</a>").insertAfter("#header-status");
    */

    // Reset the result header to its default state but not the text itself
    // because we still want to show the previous response
    let result_header = $("#result-header");
    result_header.removeClass("invoker-draw-attention");

    // One-line status bar
    $("#header-status").text(initial_header_status);

    let header_left_link_file_content = `
        <input type="button" value="New"/>
        <input type="button" value="Rename"/>
        <input type="button" value="Delete"/>
    `

    tippy('#header-left-link-file', {
        content: header_left_link_file_content,
        allowHTML: true,
        theme: 'light',
        trigger: 'click',
        placement: 'bottom',
        arrow: true,
        interactive: true,
      });

}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_data_model_area = function() {
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_document_title = function(name) {
    let new_title = `${name} - IDE - Zato`;
    document.title = new_title;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.push_url_path = function(object_type, name, name_url_safe) {
    let new_url_path = `/zato/service/ide/${object_type}/${name_url_safe}/?cluster=1`;
    history.pushState({"object_type":object_type, "name": name_url_safe}, null, new_url_path);
    $.fn.zato.ide.populate_document_title(name);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.push_service_url_path = function(name) {
    $.fn.zato.ide.push_url_path("service", name, name);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.highlight_current_file = function(fs_location) {
    $("a.fs-location-link").each(function(idx) {
        let title = $(this).attr("title");
        if(title == fs_location) {
            $.fn.zato.toggle_css_class(this, "zato-invalid", "current");
        }
        else {
            $.fn.zato.toggle_css_class(this, "current", "zato-invalid");
        }
    });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_current_file_service_list = function(current_file_service_list, new_service_name) {

    // For later use
    var first_option_elem = null;
    var has_new_service_name_match = false;

    // First, remove anything we already have in the list ..
    $(".option-current-file").remove();

    // .. get a reference to the parent optgroup ..
    let optgroup = $("#optgroup-current-file");

    // .. and populate it anew
    for (const item of current_file_service_list) {

        var option = $("<option>");
        option.text(item.name);
        option.attr("class", "option-current-file");
        option.attr("data-fs-location", item.fs_location);
        option.attr("data-line-number", item.line_number_human);
        option.attr("data-is-current-file", "1");
        option.appendTo(optgroup);

        if(first_option_elem === null) {
            first_option_elem = option;
        }

        // This will match only if we have a meaningful new service name on input,
        // which will be the case with "on-service-selected" handlers only
        // but not with "on-file-selected" ones.
        if(item.name == new_service_name) {
            option.attr("selected", "selected");
            has_new_service_name_match = true;
        }
    }

    // This will be entered only by the "on-file-selected" handlers
    // because they do not have any specific service to select.
    if(!has_new_service_name_match) {
        first_option_elem.attr("selected", "selected");
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_source_object = function(object_type, name, fs_location) {
    var callback = function(data, status) {
        let msg = data.responseText;
        let json = JSON.parse(msg)
        let current_file_source_code = json.current_file_source_code;
        $.fn.zato.ide.load_editor_session(fs_location, current_file_source_code);
        $.fn.zato.ide.highlight_current_file(fs_location);
        $.fn.zato.ide.populate_current_file_service_list(json.current_file_service_list, name);
    }

    var url = String.format('/zato/service/ide/get-{0}/{1}/', object_type, name);
    $.fn.zato.post(url, callback);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_cluster_name = function() {
    return $("#cluster_name").val();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_fs_location = function() {
    return $("#current_fs_location").val();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_current_fs_location = function(fs_location) {
    $("#current_fs_location").val(fs_location);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_source_code_key = function() {
    return $.fn.zato.ide.get_cluster_name() + "." + $.fn.zato.ide.get_current_fs_location();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_document_changed = function(e) {
    let undo_manager = window.zato_editor.getSession().getUndoManager();
    let has_undo = undo_manager.hasUndo();
    $.fn.zato.ide.mark_file_modified(has_undo);

    // Make sure there is no selection if there is no undo
    // because there may be some in case the edit we have just undone
    // had come from LocalStorate, in which case it overwrote the whole document,
    // thus making everything use a yellow background which is not necessary.
    if(!has_undo) {
        window.zato_editor.clearSelection()
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.mark_file_modified = function(has_undo) {

    // There will be only one such element but it will not have an ID, hence the iteration.
    $("a.fs-location-link.current").each(function() {
        var elem = $(this);
        var file_name = elem.attr("data-file-name");
        if(has_undo) {
            file_name += " *";
            elem.addClass("modified");
        }
        else {
            elem.removeClass("modified");
        }
        elem.text(file_name);
    })
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_up_editor_session = function(editor_session) {
    editor_session.setMode("ace/mode/python");
    editor_session.setUndoSelect(true);
    editor_session.on("change", $.fn.zato.ide.on_document_changed);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_editor_session = function(fs_location, current_file_source_code) {
    var editor_session = window.zato_editor_session_map[fs_location];
    if(!editor_session) {
        var editor_session = ace.createEditSession(current_file_source_code);
    }
    $.fn.zato.ide.set_up_editor_session(editor_session);
    window.zato_editor.setSession(editor_session);
    window.zato_editor.focus();
}

$.fn.zato.ide.save_current_editor_session = function() {
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    window.zato_editor_session_map[current_fs_location] = window.zato_editor.getSession();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_selected = function(fs_location, fs_location_url_safe) {
    $.fn.zato.ide.save_current_editor_session();
    $.fn.zato.ide.set_current_fs_location(fs_location);
    $.fn.zato.ide.push_url_path("file", fs_location, fs_location_url_safe);
    $.fn.zato.ide.load_source_object("file", fs_location, fs_location);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_service_select_changed_current_file = function(option_selected) {

    let fs_location = option_selected.attr('data-fs-location');
    var line_number = option_selected.attr('data-line-number');

    let should_center = false;
    let should_animate = true;
    let callback_function = null;

    window.zato_editor.scrollToLine(line_number, should_center, should_animate, callback_function);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_service_select_changed_non_current_file = function(select_elem, option_selected) {
    let new_service_name = select_elem.value;
    let fs_location = option_selected.attr('data-fs-location');
    $.fn.zato.ide.save_current_editor_session();
    $.fn.zato.ide.set_current_fs_location(fs_location);
    $.fn.zato.ide.push_service_url_path(new_service_name);
    $.fn.zato.ide.load_source_object("service", new_service_name, fs_location);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_service_select_changed = function(select_elem) {
    let option_selected = $('option:selected', select_elem);
    let is_current_file = option_selected.attr('data-is-current-file') == "1";

    if(is_current_file) {
        $.fn.zato.ide.on_service_select_changed_current_file(option_selected);
    }
    else {
        $.fn.zato.ide.on_service_select_changed_non_current_file(select_elem, option_selected);
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.get_sync_deploy_request_url = function() {
    let input = $("#current_fs_location");
    let current_fs_location = input.val();
    let out = "/zato/service/deploy/?current_fs_location="+ current_fs_location;
    return out
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_deploy_submitted = function() {

    const options = {
        "request_form_id": "#editor-form",
        "on_started_activate_blinking": ["#deploying-please-wait"],
        "on_ended_draw_attention": ["#result-header"],
        "get_request_url_func": $.fn.zato.invoker.get_sync_deploy_request_url,

    }
    $.fn.zato.invoker.run_sync_deployer(options);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.run_sync_deployer = function(options) {
    //$.fn.zato.invoker.run_sync_form_submitter(options);
    //options = $.fn.zato.to_dict(options);
    //console.log("Opt: "+ options);

    // Populate the form based on what is inside the editor
    let editor_value = window.zato_editor.getSession().getValue()
    $("#data-editor").val(editor_value);

    $.fn.zato.invoker.run_sync_form_submitter(options);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
