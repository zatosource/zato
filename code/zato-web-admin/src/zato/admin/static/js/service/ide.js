
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$(document).ready(function() {
    $("#invoke-service").click($.fn.zato.invoker.on_invoke_submitted);
    $("#header-left-link-deploy").click($.fn.zato.invoker.on_deploy_submitted);
});

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.init_editor = function(initial_header_status) {

    // Global variables
    window.zato_undeployed_prefix = "🔷 ";

    // All the keys that we use with LocalStorage
    window.zato_local_storage_key = {
        "zato_action_area_size": "zato.action-area-size",
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
        fontFamily: "Zato_IDE_Font",
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
    hotkeys("F2", $.fn.zato.ide.on_key_toggle_action_area);

    // Same as above (F2)
    window.zato_editor.commands.addCommand({
        name: "on_F2",
        bindKey: {win: "F2",  mac: "F2"},
        exec: function(_ignored_editor) {
            $.fn.zato.ide.on_key_toggle_action_area(null, null);
        }
    })

    // Ignore F1
    window.zato_editor.commands.addCommand({
        name: "on_F21",
        bindKey: {win: "F21",  mac: "F21"},
        exec: function(_ignored_editor) {
            // Explicitly do nothing
        }
    })

    // Ctrl-S to deploy a file
    document.addEventListener("keydown", e => {
        if ((e.ctrlKey || e.metaKey) && e.key === "s") {
          e.preventDefault();
          $.fn.zato.ide.on_key_deploy_file(null, null);
        }
      });

    // Ctrl-Enter to invoke a service
    document.addEventListener("keydown", e => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
          e.preventDefault();
          $.fn.zato.ide.on_key_invoke(null, null);
        }
      });

    // Make sure the menu can be visible
    $(".pure-css-nav").hover(function() {
        $(".pure-css-nav").addClass("position-relative");
    });
    $(".pure-css-nav").mouseleave(function() {
        $(".pure-css-nav").removeClass("position-relative");
    });

    // This will try to load all the remember layout options from LocalStorage
    $.fn.zato.ide.restore_layout();

    // This will try to load the content from LocalStorage
    $.fn.zato.ide.load_current_source_code_from_local_storage();

    // Optionally, populate the initial deployment state
    $.fn.zato.ide.maybe_populate_initial_last_deployed()

    // Optionally, indicate that there are some unsaved changes that can be deployed
    $.fn.zato.ide.maybe_set_deploy_needed();

    window.zato_inactivity_interval = null;
    document.onkeydown = $.fn.zato.ide.reset_inactivity_timeout;
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
    //  console.log("Handing inactivity")
    $.fn.zato.ide.save_current_source_code_to_local_storage();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.save_current_source_code_to_local_storage = function() {
    //  console.log("Saving to local storage")
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
$.fn.zato.ide.on_key_toggle_action_area = function(_ignored_event, _ignored_handler) {
    $.fn.zato.ide.toggle_action_area();
}

// Deploys the current file
$.fn.zato.ide.on_key_deploy_file = function(_ignored_event, _ignored_handler) {
    $.fn.zato.invoker.on_deploy_submitted();
}

// Invokes the current service
$.fn.zato.ide.on_key_invoke = function(_ignored_event, _ignored_handler) {
    $.fn.zato.invoker.on_invoke_submitted();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.toggle_action_area = function() {

    // let default_size = "3.9fr 1fr 0.06fr";
    // let expanded_size = "1.0fr 1fr 0.06fr";

    let object_select = $("#object-select");

    let default_size = "1.0fr 1fr 0.06fr";
    let expanded_size = "3.9fr 1fr 0.06fr";

    let elem_to_expand = $("#action-area-header");
    let is_expanded = elem_to_expand.attr("data-is-expanded");

    if(is_expanded == "false") {
        new_size = expanded_size;
        elem_to_expand.attr("data-is-expanded", "true");
        $.fn.zato.toggle_css_class(object_select, "expanded", "default");
    }
    else {
        new_size = default_size
        elem_to_expand.attr("data-is-expanded", "false");
        $.fn.zato.toggle_css_class(object_select, "default", "expanded");
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

$.fn.zato.ide.get_header_links_elem = function(prefix) {
    let header_links_id = `#header-links-${prefix}`;
    let header_links = $(header_links_id);
    return header_links;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.clear_header_links = function(prefix) {

    // The element where all the links reside ..
    let header_links = $.fn.zato.ide.get_header_links_elem(prefix);

    // .. clean it up.
    header_links.empty();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.add_header_link = function(prefix, item_label, text, is_last) {

    // The element where all the links reside ..
    let header_links = $.fn.zato.ide.get_header_links_elem(prefix);

    // .. this is what each link will be based on ..
    let link_pattern = `<input type="button" id="header-{0}-link-{1}" value="{2}"></button>`;

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

$.fn.zato.ide.add_header_span = function(prefix, id, is_visible) {

    if(is_visible) {
        var class_ = "visible";
    }
    else {
        var class_ = "hidden";
    }

    let span = `<span id=${id} class="${class_}"></span>`;
    let header_links = $.fn.zato.ide.get_header_links_elem(prefix);

    header_links.append($(span));
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
    $(".file-listing-tr").hide();
    $(".invoker-tr").show();

    // Left-hand side links
    // $.fn.zato.ide.add_header_left_link("deploy", "Deploy");
    $.fn.zato.ide.add_header_left_link("file", "File");
    // $.fn.zato.ide.add_header_left_link("deploy-all-changed", "Deploy all changed");
    //$.fn.zato.ide.add_header_left_link("previous", "◄ Req.");
    //$.fn.zato.ide.add_header_left_link("next", "Req. ►", true);
    // $.fn.zato.ide.add_header_left_link("clear-request", "Clear request", true);

    // Right-hand side links
    //$.fn.zato.ide.add_header_right_link("open-api", "OpenAPI", true);
    //$.fn.zato.ide.add_header_right_link("push", "Push");
    //$.fn.zato.ide.add_header_right_link("push-all", "Push all", true);

    // One-line status bar
    // $("#header-status").text("curl http://api:api@10.151.19.39:11223/zato/api/api.adapter.crm.customer.create -d "{\"customer_id\":\"123\"}'");
    /*
    $("#header-status").text("curl http://api:api@10.151.19.39:11223/zato/api/api.adapter.crm.customer.create -d "{\"customer_id\":\"123\"}'");
    $("<a href=\"#\">Edit</a>").insertAfter("#header-status");
    $("<a class=\"header-sublink-first\" href=\"#\">Copy</a>").insertAfter("#header-status");
    */

    // Reset the result header to its default state but not the text itself
    // because we still want to show the previous response
    let result_header = $("#result-header");
    result_header.removeClass("invoker-draw-attention");

    // One-line status bar
    $("#header-status").text(initial_header_status);

    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    if(current_fs_location) {
        var button_attrs = "";
    }
    else {
        var button_attrs = `disabled="disabled" class="no-click"`;
    }

    let header_left_link_file_content = `
        <input type="button" id="file-new" value="New" onclick="$.fn.zato.ide.on_file_new()";/>
        <input type="button" id="file-reload" value="Reload" ${button_attrs} onclick="$.fn.zato.ide.on_file_reload();"/>
        <input type="button" id="file-rename" value="Rename" ${button_attrs} onclick="$.fn.zato.ide.on_file_rename();"/>
        <input type="button" id="file-delete" value="Delete" ${button_attrs} onclick="$.fn.zato.ide.on_file_delete();"/>
    `;

    tippy("#header-left-link-file", {
        content: header_left_link_file_content,
        allowHTML: true,
        theme: "light",
        trigger: "click",
        placement: "bottom",
        arrow: true,
        interactive: true,
        onShown(instance) {
            $.fn.zato.ide.postprocess_file_buttons();
        }
      });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_post_load_source_func = function(data) {
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_op_error_func = function(op_name) {
    let result_header_selector = "#result-header";
    _on_error_func = function(options, jq_xhr, text_status, error_message) {
        console.log(`File ${op_name} impl, on error:  ${jq_xhr.status} -> ${error_message} ->  ${jq_xhr.responseText}`);
        $(result_header_selector).text(`${jq_xhr.status} ${error_message}`);
        $("#data-response").val(jq_xhr.responseText);
        $.fn.zato.invoker.draw_attention([result_header_selector]);
    };
    return _on_error_func;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_op_success_func = function(
    op_name,
    placeholder_verb,
    after_on_file_op_success_func,
)
{
    let _on_success_func = function(options, data) {

        console.log(`File ${op_name} impl, on success: `+ $.fn.zato.to_dict(data));

        if($.fn.zato.is_object(data)) {
            var data = data;
        }
        else {
            var data = $.parseJSON(data);
        }

        _get_current_file_service_list_func = function() {
            let item = {}
            item.fs_location = "";
            item.fs_location_url_safe = "";
            item.line_number_human = -1;
            item.line_number_human = -1;
            item.current_root_directory = "zato-undefined";
            item.root_directory_count = -1;
            item.name = `(${placeholder_verb} ..)`;

            let out = [item];
            return out;
        }

        $.fn.zato.show_bottom_tooltip(`#file-${op_name}`, `${placeholder_verb} ..`, true);
        $.fn.zato.ide.set_current_fs_location(data.full_path);
        $.fn.zato.ide.on_file_selected(
            data.full_path,
            data.full_path_url_safe,
            false,
            false,
            null, // _get_current_file_service_list_func,
        );
        if(after_on_file_op_success_func) {
            after_on_file_op_success_func();
        }
    };
    return _on_success_func;
};

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_file_reloaded = function() {

    // Local variables
    let elem_id_selector = "#file-reload";
    let text = "OK, reloaded";

    // Do show the tooltip now
    $.fn.zato.show_bottom_tooltip(elem_id_selector, text);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_file_created = function() {

    // Local variables
    let main_elem_id_selector = "#file-new";
    let main_text = "OK, created";
    let invoke_elem_id_selector = "#invoke-service";
    let invoke_text = "Click here to invoke";

    // Do show the tooltips now
    $.fn.zato.show_bottom_tooltip(main_elem_id_selector, main_text);
    $.fn.zato.show_left_tooltip(invoke_elem_id_selector, invoke_text);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_file_renamed = function() {

    // Local variables
    let elem_id_selector = "#file-rename";
    let text = "OK, renamed";

    // Do show the tooltip now
    $.fn.zato.show_bottom_tooltip(elem_id_selector, text);

    // We have already switched to demo.py so we need to disable buttons that would rename or delete it
    $.fn.zato.ide.disable_file_rename_button();
    $.fn.zato.ide.disable_file_delete_button();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.after_file_deleted = function() {

    // Local variables
    let elem_id_selector = "#file-delete";
    let text = "OK, deleted";

    // Do show the tooltip now
    $.fn.zato.show_bottom_tooltip(elem_id_selector, text);

    // We have already switched to demo.py so we need to disable buttons that would rename or delete it
    $.fn.zato.ide.disable_file_rename_button();
    $.fn.zato.ide.disable_file_delete_button();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_simple_impl = function(
    current_root_directory,
    file_name,
    current_file_name_field,
    new_file_name,
    url_path,
    form_id,
    options,
    display_timeout,
    op_name,
    placeholder_verb,
    after_on_file_op_success_func_impl
) {

    // Local variables
    let after_on_file_op_success_func = function() {
        $.fn.zato.ide.populate_current_file_service_list_impl(after_on_file_op_success_func_impl, "1");
    }

    let _on_success_func = $.fn.zato.ide.on_file_op_success_func(op_name, placeholder_verb, after_on_file_op_success_func);
    let _on_error_func = $.fn.zato.ide.on_file_op_error_func(op_name);

    $.fn.zato.ide.build_singleton_form(form_id, {
        [current_file_name_field]: file_name,
        "new_file_name": new_file_name,
        "root_directory": current_root_directory,
    });

    $.fn.zato.invoker.submit_form(
        url_path,
        "#"+form_id,
        options,
        _on_success_func,
        _on_error_func,
        display_timeout,
        "json"
    );
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_new_impl = function(current_root_directory, file_name) {

    let url_path = "/zato/service/ide/create-file/";
    let form_id = "file-new-form";
    let options = {};
    let display_timeout = 1;
    let op_name = "new";
    let placeholder_verb = "Deploying"
    let after_on_file_op_success_func_impl = $.fn.zato.ide.after_file_created;

    $.fn.zato.ide.on_file_simple_impl(
        current_root_directory,
        file_name,
        "file_name",
        null,
        url_path,
        form_id,
        options,
        display_timeout,
        op_name,
        placeholder_verb,
        after_on_file_op_success_func_impl,
    )
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_new = function() {

    // Local variables
    let prompt_text = "Create a new file."
    let root_directory_count = $.fn.zato.ide.get_root_directory_count();
    let current_root_directory = $.fn.zato.ide.get_current_root_directory();

    // We need an integer here ..
    root_directory_count = Number(root_directory_count);

    // .. show additional information if we have more than one root directory ..
    if(root_directory_count > 1) {
        prompt_text += "\n\n";
        prompt_text += `Root directory: ${current_root_directory}\n\n`;
    }

    // .. do prompt the user ..
    let file_name = prompt(prompt_text, "");

    // .. proceed if we've received anything ..
    if(file_name) {
        console.log(`Creating file: "${current_root_directory}" -> "${file_name}"`);
        $.fn.zato.ide.on_file_new_impl(current_root_directory, file_name);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_rename_impl = function(current_root_directory, current_file_name, new_file_name) {

    let url_path = "/zato/service/ide/rename-file/";
    let form_id = "file-rename-form";
    let options = {};
    let display_timeout = 1;
    let op_name = "rename";
    let placeholder_verb = "Renaming"
    let after_on_file_op_success_func_impl = $.fn.zato.ide.after_file_renamed;

    $.fn.zato.ide.on_file_simple_impl(
        current_root_directory,
        current_file_name,
        "current_file_name",
        new_file_name,
        url_path,
        form_id,
        options,
        display_timeout,
        op_name,
        placeholder_verb,
        after_on_file_op_success_func_impl,
    )
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_rename = function() {

    // Local variables
    let prompt_text = "Enter new file name.";
    let fs_location = $.fn.zato.ide.get_current_fs_location();
    let root_directory_count = $.fn.zato.ide.get_root_directory_count();
    let current_root_directory = $.fn.zato.ide.get_current_root_directory();

    let current_file_name = fs_location.replace(current_root_directory, "");
    if(current_file_name.charAt(0) === '/' || current_file_name.charAt(0) === '\\') {
        current_file_name = current_file_name.substring(1);
    }

    // We need an integer here ..
    root_directory_count = Number(root_directory_count);

    // .. show additional information if we have more than one root directory ..
    if(root_directory_count > 1) {
        prompt_text += "\n\n";
        prompt_text += `Root directory: ${current_root_directory}\n\n`;
    }

    // .. do prompt the user ..
    let new_file_name = prompt(prompt_text, current_file_name);

    // .. proceed if we've received anything ..
    if(new_file_name) {
        if(new_file_name != current_file_name) {
            console.log(`Rename file: "${current_root_directory}" -> "${current_file_name} -> "${new_file_name}"`);
            $.fn.zato.ide.on_file_rename_impl(current_root_directory, current_file_name, new_file_name);
        }
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_delete_impl = function(fs_location) {

    // Local variables
    let after_on_file_op_success_func = function() {
        $.fn.zato.ide.populate_file_list($.fn.zato.ide.after_file_deleted);
        console.log(`Deleted "${fs_location}"`);
    }

    let url_path = "/zato/service/ide/delete-file/";
    let form_id = "file-delete-form";
    let options = {};
    let display_timeout = 1;
    let _on_success_func = $.fn.zato.ide.on_file_op_success_func("delete", "Deleting", after_on_file_op_success_func);
    let _on_error_func = $.fn.zato.ide.on_file_op_error_func("delete");

    $.fn.zato.ide.build_singleton_form(form_id, {
        "fs_location": fs_location,
    });

    $.fn.zato.invoker.submit_form(
        url_path,
        "#"+form_id,
        options,
        _on_success_func,
        _on_error_func,
        display_timeout,
        "json"
    );
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_delete = function() {

    // Local variables
    let current_object_select = $.fn.zato.ide.get_current_object_select();
    let fs_location = current_object_select.attr("data-fs-location");
    let fs_location_url_safe = current_object_select.attr("data-fs-location-url-safe");
    let prompt_text = `Confirm file deletion.\n\n${fs_location}`;

    if(confirm(prompt_text)) {
        console.log(`Deleting file: "${fs_location}" "${fs_location_url_safe}"`)
        $.fn.zato.ide.on_file_delete_impl(fs_location);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_reload = function() {
    let current_object_select = $.fn.zato.ide.get_current_object_select();
    let fs_location = current_object_select.attr("data-fs-location");
    let fs_location_url_safe = current_object_select.attr("data-fs-location-url-safe");
    console.log(`Reloading file: "${fs_location}" "${fs_location_url_safe}"`)
    $.fn.zato.ide.on_file_selected(
        fs_location,
        fs_location_url_safe,
        false,
        $.fn.zato.ide.after_file_reloaded,
        null,
        "should_convert_pickup_to_work_dir=True",
    );
}


/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_info = function() {

    // Local variables
    let form_id = "file-info-form";
    let fs_location = $.fn.zato.ide.get_current_fs_location();

    console.log(`Getting file info for: "${fs_location}"`);

    // First, build a dynamic form ..
    $.fn.zato.ide.build_singleton_form(form_id, {
        "fs_location": fs_location,
    });

    // .. collect all the required parameters ..
    const options = {
        "request_form_id": `#${form_id}`,
        "on_started_activate_blinking": ["#getting-info-please-wait"],
        "on_ended_draw_attention": ["#result-header"],
        "get_request_url_func": $.fn.zato.invoker.get_sync_deploy_request_url,
        "on_post_success_func": $.fn.zato.ide.on_post_success_func,
    }

    // .. and invoke the newly created form now.
    $.fn.zato.invoker.run_sync_form_submitter(options);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.build_singleton_form = function(form_id, items) {

    // Local variables
    let form_selector = `#${form_id}`;
    let parent = $("#singleton-form-parent");

    // First, make sure that such an element doesn't exist ..
    $(form_selector).remove();

    // .. now, create it again ..
    let form = `<form id="${form_id}" method="post"></form>`;

    // .. append it to our parent ..
    parent.append(form);

    // .. get a handle to the newly created form ..
    let form_elem = $(form_selector);

    // .. go through all the fields that we need to create ..
    for(const [key, value] of Object.entries(items)) {

        // .. create a hidden field for each one ..
        let field = `<input type="hidden" name="${key}" value="${value}"/>`;

        // .. and attach it to the form.
        form_elem.append(field);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.populate_document_title = function(name) {
    var prefix = "";
    let has_modified =  $.fn.zato.ide.has_current_object_modified();

    // console.log("Received has modified: "+ has_modified);

    if(has_modified) {
        prefix = "* ";
    }

    let new_title = `${prefix}${name} - IDE - Zato`;
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

    // console.log("Populate current file service list: "+ current_file_service_list);

    // First, remove anything we already have in the list ..
    $(".option-current-file").remove();

    // .. get a reference to the parent optgroup ..
    let optgroup = $("#optgroup-current-file");

    // .. and populate it anew
    for (const item of current_file_service_list) {

        console.log("Populate current file item: "+ $.fn.zato.to_dict(item));

        var option = $("<option>");
        option.text(item.name);
        option.attr("class", "option-current-file");
        option.attr("data-service-name", item.name);
        option.attr("data-fs-location", item.fs_location);
        option.attr("data-fs-location-url-safe", item.fs_location_url_safe);
        option.attr("data-line-number", item.line_number_human);
        option.attr("data-is-current-file", "1");
        option.attr("data-current-root-directory", item.current_root_directory);
        option.attr("data-root-directory-count", item.root_directory_count);
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

            // If we are here, it means that the current service can be invoked
            $.fn.zato.ide.enable_invoke_button();
        }
    }

    // This will be entered only by the "on-file-selected" handlers
    // because they do not have any specific service to select.
    if(!has_new_service_name_match) {
        if(first_option_elem) {
            first_option_elem.attr("selected", "selected");
        }
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_is_current_file = function(current_fs_location) {

    //  console.log("Setting current file: "+ current_fs_location);

    // Zero out the current file flag for all the select opions ..
    $(`option[data-object-holder="1"]`).attr("data-is-current-file", "0");

    // and enable it back for the ones that point to the current file
    $(`option[data-fs-location="${current_fs_location}"`).attr("data-is-current-file", "1");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.enable_button = function(button_id) {

    // Local variables
    let button = $(button_id);

    // Make it possible to use the button
    button.removeAttr("disabled");
    button.removeClass("no-click");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.disable_button = function(button_id) {

    // Local variables
    let button = $(button_id);

    // Disable the button
    button.attr("disabled", "disabled");
    button.addClass("no-click");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.enable_invoke_button = function() {
    $.fn.zato.ide.enable_button("#invoke-service");
}

$.fn.zato.ide.enable_file_rename_button = function() {
    $.fn.zato.ide.enable_button("#file-rename");
}

$.fn.zato.ide.enable_file_delete_button = function() {
    $.fn.zato.ide.enable_button("#file-delete");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.disable_invoke_button = function() {
    $.fn.zato.ide.disable_button("#invoke-service");
}

$.fn.zato.ide.disable_file_rename_button = function() {
    $.fn.zato.ide.disable_button("#file-rename");
}

$.fn.zato.ide.disable_file_delete_button = function() {
    $.fn.zato.ide.disable_button("#file-delete");
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.postprocess_file_buttons = function() {

    // Local variables
    let button_id_list = ["#file-rename", "#file-delete", "#file-reload"];
    let current_object_type = $.fn.zato.ide.get_current_object_type();

    // Check if we have any specific file now that we loaded an object
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();

    // console.log(`Postprocessing file buttons: "${current_fs_location}"`);

    // Go through all the buttons ..
    for(button_id of button_id_list) {

        // First, clear out everything ..
        $.fn.zato.ide.enable_button(button_id);

        // .. we enter here if we don't have any current file ..
        if(!current_fs_location) {

            // .. now, indicate that this button should be disabled.
            $.fn.zato.ide.disable_button(button_id);
        }

        // .. certain buttons are disabled if we're showing services ..
        //
        let is_service = current_object_type == "service";
        let is_demo = current_fs_location.endsWith("demo.py");
        if(is_service || is_demo) {
            $.fn.zato.ide.disable_file_rename_button();
            $.fn.zato.ide.disable_file_delete_button();
        }
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.post_load_source_object = function(
    data,
    object_name,
    current_file_source_code,
    current_file_service_list,
    fs_location,
    reuse_source_code,
    after_post_load_source_func,
    get_current_file_service_list_func,
) {
    $.fn.zato.ide.load_editor_session(fs_location, current_file_source_code, reuse_source_code);
    $.fn.zato.ide.highlight_current_file(fs_location);
    if(get_current_file_service_list_func) {
        current_file_service_list = get_current_file_service_list_func();
    }
    $.fn.zato.ide.populate_current_file_service_list(current_file_service_list, object_name);

    console.log(`Object: "${object_name}", reuse:"${reuse_source_code}"`); // current:"${$.fn.zato.to_dict(current_file_service_list)}"`);

    // We are going to reuse the source that we may already have cached
    // and it means that we may potentially need to set the correct deployment status ..
    if(reuse_source_code) {
        $.fn.zato.ide.maybe_populate_initial_last_deployed();
        $.fn.zato.ide.maybe_set_deploy_needed();
    }

    // .. if we are here, we know that we have just loaded the latest source code
    // .. from the server so we also know that we don't need to deploy this file.
    else {
        $.fn.zato.ide.set_deployment_button_status_not_different();
        $.fn.zato.ide.update_deployment_option_state(false);
    }

    $.fn.zato.ide.set_is_current_file(fs_location);
    if(after_post_load_source_func) {
        after_post_load_source_func(data);
    }

    // This will enable or disable file buttons
    $.fn.zato.ide.postprocess_file_buttons();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_source_object = function(
    object_type,
    object_name,
    fs_location,
    reuse_source_code,
    after_post_load_source_func,
    get_current_file_service_list_func,
    extra_qs,
) {

    extra_qs = extra_qs || "";

    var callback = function(data, _unused_status) {
        let msg = data.responseText;
        let json = JSON.parse(msg)
        let current_file_source_code = json.current_file_source_code;
        let current_file_service_list = json.current_file_service_list;
        $.fn.zato.ide.post_load_source_object(
            data,
            object_name,
            current_file_source_code,
            current_file_service_list,
            fs_location,
            reuse_source_code,
            after_post_load_source_func,
            get_current_file_service_list_func
        );
    }

    var url = String.format("/zato/service/ide/get-{0}/{1}/?1=1&{2}", object_type, object_name,extra_qs);
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

$.fn.zato.ide.get_current_root_directory = function() {
    return $("#current_root_directory").val();
}

$.fn.zato.ide.set_current_root_directory = function(value) {
    $("#current_root_directory").val(value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_root_directory_count = function() {
    return $("#root_directory_count").val();
}

$.fn.zato.ide.set_root_directory_count = function(value) {
    $("#root_directory_count").val(value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_source_code_key = function() {
    return $.fn.zato.ide.get_cluster_name() + "." + $.fn.zato.ide.get_current_fs_location();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_last_deployed_key = function() {
    let key = "zato.last-deployed." + $.fn.zato.ide.get_current_source_code_key()
    return key;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_object_type = function() {
    let current = $("#current-object-type").val();
    return current;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.set_current_object_type = function(value) {
    $("#current-object-type").val(value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_current_object_select = function() {
    let current = $("#object-select :selected");
    //  console.log("Returning current select: "+ current.text())
    return current;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.has_current_object_modified = function() {
    let current = $.fn.zato.ide.get_current_object_select();

    let has_modified = current.attr("data-is-modified") == "1";
    // console.log("Has current modified: "+ has_modified);
    return has_modified;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_document_changed = function(e) {
    let undo_manager = window.zato_editor.getSession().getUndoManager();
    let has_undo = undo_manager.hasUndo();
    // $.fn.zato.ide.mark_file_modified(has_undo);
    $.fn.zato.ide.on_editor_changed();

    // Make sure there is no selection if there is no undo
    // because there may be some in case the edit we have just undone
    // had come from LocalStorage, in which case it overwrote the whole document,
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
    editor_session.setUndoSelect(false);
    editor_session.on("change", $.fn.zato.ide.on_document_changed);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_editor_session = function(
    fs_location,
    current_file_source_code,
    reuse_source_code
) {

    // We may already have a previous session for that file so we can load it here ..
    var editor_session = window.zato_editor_session_map[fs_location];
    if(!editor_session) {
        var editor_session = ace.createEditSession(current_file_source_code);
    }

    // .. we may have an old session whose source we need to overwrite with what we have on input ..
    if(!reuse_source_code) {
        window.zato_editor.setValue(current_file_source_code);
        window.zato_editor.clearSelection();
    }

    // .. configure ACE ..
    $.fn.zato.ide.set_up_editor_session(editor_session);

    // .. let it be our current editor ..
    window.zato_editor.setSession(editor_session);

    // .. that we can now switch.
    window.zato_editor.focus();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.save_current_editor_session = function() {
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    window.zato_editor_session_map[current_fs_location] = window.zato_editor.getSession();
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_last_deployed_from_store = function(key) {
    let last_deployed = store.get(key);
    // console.log("Last deployed in store: "+ !!last_deployed +"; key: "+ key);
    return last_deployed;
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.maybe_populate_initial_last_deployed = function() {

    // Check if this file has been ever deployed, if not, we need to populate
    // the store with the current contents of the file because, by definition,
    // it must be the same as the source code from the server given that we've just loaded it.
    // console.log("In maybe populate initial last deployed");
    let key = $.fn.zato.ide.get_last_deployed_key();
    last_deployed = $.fn.zato.ide.get_last_deployed_from_store(key);

    if(!last_deployed) {
        let editor_value = window.zato_editor.getValue()
        store.set(key, editor_value);
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.maybe_set_deploy_needed = function() {
    console.log("In maybe set deploy needed");
    $.fn.zato.ide.set_deployment_status();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.populate_root_directory_info_from_option = function(option) {

    // Local variables
    let current_root_directory = option.attr("data-current-root-directory");
    let root_directory_count = option.attr("data-root-directory-count");

    console.log(`Setting root dir info: "${current_root_directory}" and "${root_directory_count}"`)

    $.fn.zato.ide.set_current_root_directory(current_root_directory);
    $.fn.zato.ide.set_root_directory_count(root_directory_count);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_file_selected = function(
    fs_location,
    fs_location_url_safe,
    reuse_source_code,
    after_post_load_source_func,
    get_current_file_service_list_func,
    extra_qs,
) {
    console.log("On file selected ..")

    if(reuse_source_code == null) {
        reuse_source_code = true;
    }
    else {
        reuse_source_code = false;
    }

    $.fn.zato.ide.save_current_editor_session();
    $.fn.zato.ide.set_current_fs_location(fs_location);
    $.fn.zato.ide.push_url_path("file", fs_location, fs_location_url_safe);
    $.fn.zato.ide.load_source_object(
        "file",
        fs_location,
        fs_location,
        reuse_source_code,
        after_post_load_source_func,
        get_current_file_service_list_func,
        extra_qs
    );
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_object_select_changed_current_file = function(option_selected) {

    //  console.log("On object selected current file ..")

    let fs_location = option_selected.attr("data-fs-location");
    var line_number = option_selected.attr("data-line-number");

    let should_center = false;
    let should_animate = true;
    let callback_function = null;

    window.zato_editor.scrollToLine(line_number, should_center, should_animate, callback_function);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_object_select_changed_non_current_file = function(option_selected) {

    //  console.log("On object selected non-current file ..")

    let new_service_name = option_selected.attr("data-service-name");
    let fs_location = option_selected.attr("data-fs-location");
    $.fn.zato.ide.save_current_editor_session();
    $.fn.zato.ide.set_current_fs_location(fs_location);
    $.fn.zato.ide.push_service_url_path(new_service_name);
    $.fn.zato.ide.load_source_object("service", new_service_name, fs_location, true);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.on_object_select_changed = function(select_elem) {

    select_elem = $(select_elem);
    let option_selected = $("option:selected", select_elem);
    let is_current_file = option_selected.attr("data-is-current-file") == "1";
    let current_object_type = $.fn.zato.ide.get_current_object_type()

    // This will update the global information about what directory we are
    $.fn.zato.ide.populate_root_directory_info_from_option(option_selected);

    // Handle the selection of a service ..
    if(current_object_type == "service") {

        // .. a service within the current file was selected ..
        if(is_current_file) {
            $.fn.zato.ide.on_object_select_changed_current_file(option_selected);
        }

        // .. a service in another file was selected ..
        else {
            //  console.log("Switching to an object in another file: "+ option_selected.text());
            $.fn.zato.ide.on_object_select_changed_non_current_file(option_selected);
        }
    }

    // .. handle the selection of a file ..
    else {

        let selected_fs_location = option_selected.attr("data-fs-location");
        let selected_fs_location_url_safe = option_selected.attr("data-fs-location-url-safe");

        // .. we enter here only if we have an actual file to switch to.
        if(selected_fs_location) {
            $.fn.zato.ide.on_file_selected(selected_fs_location, selected_fs_location_url_safe);
        }
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_editor_changed = function() {
    $.fn.zato.ide.set_deployment_status();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_status = function() {

    // Get the current value of the editor ..
    let editor_value = window.zato_editor.getValue()

    // .. get the value of what was last deployed ..
    let key = $.fn.zato.ide.get_last_deployed_key();
    let last_deployed = $.fn.zato.ide.get_last_deployed_from_store(key);

    // .. check if they are different ..
    let is_different = editor_value != last_deployed;

    // console.log("Key: "+ key);
    // console.log("Editor: ["+ editor_value + "]");
    // console.log("Store: ["+ last_deployed + "]");
    // console.log("Is diff: "+ is_different);

    // .. pick the correct CSS class to set for the "Deploy" button
    if(is_different) {
        var button_class_name = "different";
    }
    else {
        var button_class_name = "not-different";
    }

    // .. set it for the button accordingly ..
    $.fn.zato.ide.set_deployment_button_status_class(button_class_name);

    // .. and for all the select options that point to the current file ..
    $.fn.zato.ide.update_deployment_option_state(is_different);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.update_deployment_option_state = function(is_different, fs_location) {

    fs_location = fs_location || $.fn.zato.ide.get_current_fs_location();
    //  console.log(`Setting option text: ${is_different} and ${fs_location}`);

    $(`#object-select option[data-fs-location="${fs_location}"]`).each(function() {
        let option = $(this);
        let text = option.text();
        if(is_different) {
            if(text.startsWith(window.zato_undeployed_prefix)) {
                new_text = text;
                is_modified = 0;
            }
            else {
                new_text = window.zato_undeployed_prefix + text;
                is_modified = 1;
            }
        }
        else {
            new_text = text.replace(window.zato_undeployed_prefix, "");;
            is_modified = 0;
        }
        option.text(new_text)
        option.attr("data-is-modified", is_modified);
        //  console.log(`Opt: ${is_modified} -> ${option.text()}`);
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_button_status_class = function(class_name) {
    let buttons = $("#header-left-link-deploy, #invoke-service-temporarily-disabled")
    buttons.removeClass("different not-different");
    buttons.addClass(class_name);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_button_status_different = function() {
    $.fn.zato.ide.set_deployment_button_status_class("different");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_button_status_not_different = function() {
    $.fn.zato.ide.set_deployment_button_status_class("not-different");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_post_success_func = function() {
    $.fn.zato.ide.set_deployment_button_status_not_different();
    $.fn.zato.ide.update_deployment_option_state(false);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.get_sync_deploy_request_url = function() {
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    let out = String.format("/zato/service/upload/?qqfile={0}&has_post=true", current_fs_location);
    return out
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.on_deploy_submitted = function() {

    const options = {
        "request_form_id": "#editor-form",
        "on_started_activate_blinking": ["#deploying-please-wait"],
        "on_ended_draw_attention": ["#result-header"],
        "get_request_url_func": $.fn.zato.invoker.get_sync_deploy_request_url,
        "on_post_success_func": $.fn.zato.ide.on_post_success_func,

    }
    $.fn.zato.invoker.run_sync_deployer(options);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.invoker.run_sync_deployer = function(options) {

    // Populate the form based on what is inside the editor
    let editor_value = window.zato_editor.getValue()
    $("#data-editor").val(editor_value);

    // Actually deploy the source code
    $.fn.zato.invoker.run_sync_form_submitter(options);

    // Save the current contents of the file for later use
    let key = $.fn.zato.ide.get_last_deployed_key();
    store.set(key, editor_value);

}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.toggle_current_object_type = function(current) {
    if(current == "service") {
        var new_current = "file";
    }
    else {
        var new_current = "service";
    }
    $.fn.zato.ide.set_current_object_type(new_current);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_undeployed_files_list = function() {

    //  console.log("Getting undeployed files list");

    let undeployed = [];
    $(`#object-select option[data-is-modified="1"`).each(function() {
        let fs_location = $(this).attr("data-fs-location");
        undeployed.push(fs_location);
    })
    return undeployed;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.mark_as_undeployed = function(undeployed) {

    for(item of undeployed) {
        $.fn.zato.ide.update_deployment_option_state(true, item)
    }
}


/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_service_list_response = function(response) {

    //
    // We're switching from files to services here.
    //

    // Local variables
    let object_select = $("#object-select");
    let undeployed = $.fn.zato.ide.get_undeployed_files_list();

    //  console.log("On service list undeployed: "+ undeployed);

    // Extract the underlying JSON ..
    let data = JSON.parse(response.responseText);

    // .. clear out the form ..
    object_select.empty();

    // .. build the expected optgroups ..
    let optgroup_current_file = `<optgroup label="Current file" id="optgroup-current-file"/>`;
    let optgroup_all_services = `<optgroup label="All services" id="optgroup-all-services"/>`;

    // .. add our optgroups to the select ..
    object_select.append(optgroup_current_file);
    object_select.append(optgroup_all_services);

    // .. extract the newly created optgroups ..
    let optgroup_current_file_object = $("#optgroup-current-file");
    let optgroup_all_services_object = $("#optgroup-all-services");

    // .. build an option element for services from the current file and append it to the "Current file" optgroup ..
    // .. we go here if there are no services in the current file ..

    if(!data.current_file_service_list.length) {

        // Build an option indicating that there are no services ..
        var option = `<option
            class="option-current-file"
            data-object-holder="1"
            data-is-current-file="1"
            data-line-number="-1"
            data-fs-location=""
            data-fs-location-url-safe=""
            data-current-root-directory="${data.current_root_directory}"
            data-root-directory-count="${data.root_directory_count}"
            data-service-name=""
            >(No services in current file)</option>`;

        // .. append it to our select ..
        optgroup_current_file_object.append(option);
    }

    // .. we go here if there are some services in the current file ..
    else {
        for(service_item of data.current_file_service_list) {

            console.log("Current file service: "+ $.fn.zato.to_dict(service_item));
            var option = `<option
                class="option-current-file"
                data-object-holder="1"
                data-is-current-file="1"
                data-line-number="${service_item.line_number_human}"
                data-fs-location="${service_item.fs_location}"
                data-fs-location-url-safe="${service_item.fs_location_url_safe}"
                data-current-root-directory="${service_item.current_root_directory}"
                data-root-directory-count="${service_item.root_directory_count}"
                data-service-name="${service_item.name}"
                >${service_item.name}</option>`;
            optgroup_current_file_object.append(option);
        }
    }

    // .. build an option element for each service and append it to the "All services" optgroup ..
    for(service_item of data.service_list) {
        let is_current_file = service_item.fs_location == data.current_fs_location ? "1" : "0";
        var option = `<option
            class="option-all-objects"
            data-object-holder="1"
            data-is-current-file="${is_current_file}"
            data-line-number="${service_item.line_number_human}"
            data-fs-location="${service_item.fs_location}"
            data-fs-location-url-safe="${service_item.fs_location_url_safe}"
            data-current-root-directory="${service_item.current_root_directory}"
            data-root-directory-count="${service_item.root_directory_count}"
            data-service-name="${service_item.name}"
            >${service_item.name}</option>`;
        optgroup_all_services_object.append(option);
    }

    // .. switch to services ..
    $.fn.zato.ide.toggle_current_object_type("file");

    // .. mark the relevant select options as undeployed ..
    $.fn.zato.ide.mark_as_undeployed(undeployed);

    // .. services can be invoked now.
    $.fn.zato.ide.enable_invoke_button();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_file_list_response = function(response) {

    //
    // We're switching from services to files here.
    //

    // Extract the underlying JSON ..
    let data = JSON.parse(response.responseText);

    // Local variables
    let object_select = $("#object-select");
    let undeployed = $.fn.zato.ide.get_undeployed_files_list();
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    let root_directory_count = Object.keys(data).length;

    // console.log("On file list undeployed: "+ undeployed);
    // console.log("File list data: "+ $.fn.zato.to_dict(data));
    // console.log("Data length: "+ root_directory_count);

    // .. clear out the form ..
    object_select.empty();

    // .. go through everything we were given ..
    Object.entries(data).forEach(([dir_name, file_list]) => {

        // .. build an options group for each directory ..
        let optgroup_id = $.fn.zato.slugify("optgroup-" + dir_name);
        let optgroup = `<optgroup label="{0}" id="{1}"/>`;

        // .. append it to the form ..
        object_select.append(String.format(optgroup, dir_name, optgroup_id));

        // .. get a reference to it so that we can use it below ..
        let optgroup_object = $("#" + optgroup_id);

        // .. go through each file in that directory, if there are any ..
        if(file_list.length) {
            for(file_item of file_list) {

                // Loop-local variables
                let selected_option;

                let file_name = file_item.file_name;
                let file_name_url_safe = file_item.file_name_url_safe;

                // .. get the file name alone ..
                let file_name_short = file_name.replace(dir_name, "");

                // .. the file may begind with a slash ..
                let first_character = file_name_short.charAt(0);

                // .. which we need to remove ..
                if(first_character == "/" || first_character == "\\") {
                    file_name_short = file_name_short.substring(1);
                }

                // .. the file may only belong to a project's directory ..
                if(file_name_short.startsWith("impl/src/")) {
                    file_name_short = file_name_short.replace("impl/src/", "");
                }
                else if(file_name_short.startsWith("impl\\src\\")) {
                    file_name_short = file_name_short.replace("impl\\src\\", "");
                }

                // .. we need to select this option if it points to the file that we currently have opened ..
                if(file_name == current_fs_location) {
                    selected_option = `selected="selected"`;
                }
                else {
                    selected_option = "";
                }

                // .. now, we can build a new option for this file ..
                let option = `<option
                    class="option-all-objects"
                    ${selected_option}
                    data-is-current-file="1"
                    data-fs-location="${file_name}"
                    data-fs-location-url-safe="${file_name_url_safe}"
                    data-current-root-directory="${dir_name}"
                    data-root-directory-count="${root_directory_count}"
                    >${file_name_short}</option>`;

                // .. and append it to the form ..
                optgroup_object.append(option);
            }
        }
        // .. if there are no files, be explicit about it.
        else {
            let option = `<option
                class="option-all-objects"
                data-is-current-file="1"
                data-fs-location=""
                data-fs-location-url-safe=""
                data-current-root-directory="${dir_name}"
                data-root-directory-count="${root_directory_count}"
                >No files</option>`;
            optgroup_object.append(String.format(option));
        }
    });

    // .. switch to files ..
    $.fn.zato.ide.toggle_current_object_type("service");

    // .. mark the relevant select options as undeployed ..
    $.fn.zato.ide.mark_as_undeployed(undeployed);

    // .. enable buttons that can be used in the files view ..
    $.fn.zato.ide.enable_file_rename_button();
    $.fn.zato.ide.enable_file_delete_button();

    // .. services cannot be invoked in the files view.
    $.fn.zato.ide.disable_invoke_button();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.post_populate_current_file_service_list_impl = function(after_func) {

    _post_func = function(response) {
        $.fn.zato.ide.on_service_list_response(response);
        if(after_func) {
            after_func();
        }
    }
    return _post_func;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.populate_current_file_service_list_impl = function(after_func, should_wait_for_services) {

    let url_path_prefix = "/zato/service/ide/get-service-list/";
    if(should_wait_for_services === undefined) {
        should_wait_for_services = "";
    }

    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    let url_path = `${url_path_prefix}?fs_location=${current_fs_location}&should_wait_for_services=${should_wait_for_services}`;

    let callback = $.fn.zato.ide.post_populate_current_file_service_list_impl(after_func);
    $.fn.zato.invoker.invoke(url_path, "", callback)
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.populate_file_list = function(after_callback_func) {
    let url_path = "/zato/service/ide/get-file-list/";
    let callback = function(response) {
        $.fn.zato.ide.on_file_list_response(response);
        if(after_callback_func) {
            after_callback_func();
        }
    }
    $.fn.zato.invoker.invoke(url_path, "", callback)
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_toggle_object_select = function() {

    let current_object_type = $.fn.zato.ide.get_current_object_type();

    // We are switching from services to files ..
    if(current_object_type == "service") {
        $.fn.zato.ide.populate_file_list();
    }

    // .. or from files to services.
    else {
        $.fn.zato.ide.populate_current_file_service_list_impl()
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
