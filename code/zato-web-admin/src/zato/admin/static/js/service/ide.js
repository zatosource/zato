
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

let Copy_Tooltip_Timeout = 1000;

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
        "zato_request_history": "zato.request-history",
    }

    // Request history tracking
    window.zato_request_history_index = -1;

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

    // Ctrl-Up/Down to navigate request history in the textarea
    $("#data-request").on("keydown", function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === "ArrowUp") {
            e.preventDefault();
            $.fn.zato.ide.on_request_history_up();
        } else if ((e.ctrlKey || e.metaKey) && e.key === "ArrowDown") {
            e.preventDefault();
            $.fn.zato.ide.on_request_history_down();
        } else if ((e.ctrlKey || e.metaKey) && e.key === "k") {
            e.preventDefault();
            $.fn.zato.ide.open_history_overlay();
        }
    });

    // Ctrl-K globally to open history overlay
    document.addEventListener("keydown", e => {
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
          e.preventDefault();
          $.fn.zato.ide.open_history_overlay();
        }
      });

    // Make sure the menu can be visible
    $(".pure-css-nav").hover(function() {
        $(".pure-css-nav").addClass("position-relative");
    });
    $(".pure-css-nav").mouseleave(function() {
        $(".pure-css-nav").removeClass("position-relative");
    });


    // Set the initial baseline for deployment status from the current editor content BEFORE loading from localStorage
    let key = $.fn.zato.ide.get_last_deployed_key();
    let editor_value = window.zato_editor.getValue();
    console.log("init_editor: setting initial baseline with key:", JSON.stringify(key));
    console.log("init_editor: editor_value length:", editor_value ? editor_value.length : null);
    localStorage.setItem(key, editor_value);
    console.log("init_editor: initial baseline set");

    // This will try to load the content from LocalStorage
    $.fn.zato.ide.load_current_source_code_from_local_storage();

    window.zato_inactivity_interval = null;
    document.onkeydown = $.fn.zato.ide.reset_inactivity_timeout;

    $.fn.zato.ide.update_request_history_buttons();

    let is_mac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    let modifier_key = is_mac ? '⌘' : 'Ctrl';
    let placeholder_text = "Enter parameters as key=value pairs, e.g.:\nkey1=value1\nkey2=value2\n\n" +
                          modifier_key + "+↑/↓ to browse history\n" +
                          modifier_key + "+K for full history";
    $("#data-request").attr("placeholder", placeholder_text);

    $.fn.zato.ide.init_resizer();

    let actionAreaContainer = document.getElementById('action-area-container');
    let actionArea = document.getElementById('action-area');

    function resizeDataResponse() {
        let dataResponse = document.getElementById('data-response');
        if (!dataResponse) return;

        let actionAreaHeight = actionArea.offsetHeight;
        let dataResponseTop = dataResponse.getBoundingClientRect().top;
        let actionAreaTop = actionArea.getBoundingClientRect().top;
        let offsetFromTop = dataResponseTop - actionAreaTop;
        let availableHeight = actionAreaHeight - offsetFromTop - 10;

        if (availableHeight > 100) {
            dataResponse.style.height = availableHeight + 'px';
        }
    }

    let dataRequest = document.getElementById('data-request');
    if (dataRequest) {
        let actionAreaHeight = actionArea.offsetHeight;
        let maxHeight = actionAreaHeight - 200;
        dataRequest.style.maxHeight = maxHeight + 'px';

        let savedHeight = store.get('zato.data-request-height');
        if (savedHeight) {
            dataRequest.style.height = savedHeight;
        }

        let resizeIndicator = document.createElement('div');
        resizeIndicator.textContent = '⋯';
        resizeIndicator.style.cssText = 'position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); font-size: 20px; color: red; pointer-events: none; padding: 0 5px; z-index: 10;';
        dataRequest.parentElement.style.position = 'relative';
        dataRequest.parentElement.appendChild(resizeIndicator);

        function updateIndicatorPosition() {
            let rect = dataRequest.getBoundingClientRect();
            let parentRect = dataRequest.parentElement.getBoundingClientRect();
            let top = rect.bottom - parentRect.top - 3;
            resizeIndicator.style.top = top + 'px';
        }
        updateIndicatorPosition();

        let isResizingTextarea = false;
        let startY = 0;
        let startHeight = 0;

        dataRequest.addEventListener('mousemove', function(e) {
            if (isResizingTextarea) return;

            let rect = dataRequest.getBoundingClientRect();
            let bottomEdge = rect.bottom;
            let mouseY = e.clientY;

            if (Math.abs(mouseY - bottomEdge) < 10) {
                dataRequest.style.cursor = 'ns-resize';
                dataRequest.style.borderBottomColor = '#999';
                resizeIndicator.style.color = 'green';
            } else {
                dataRequest.style.cursor = '';
                dataRequest.style.borderBottomColor = '#ccc';
                resizeIndicator.style.color = 'red';
            }
        });

        dataRequest.addEventListener('mouseleave', function() {
            if (!isResizingTextarea) {
                dataRequest.style.cursor = '';
                dataRequest.style.borderBottomColor = '#ccc';
                resizeIndicator.style.color = 'red';
            }
        });

        dataRequest.addEventListener('mousedown', function(e) {
            let rect = dataRequest.getBoundingClientRect();
            let bottomEdge = rect.bottom;
            let mouseY = e.clientY;

            if (Math.abs(mouseY - bottomEdge) < 10) {
                isResizingTextarea = true;
                startY = e.clientY;
                startHeight = dataRequest.offsetHeight;
                e.preventDefault();
            }
        });

        document.addEventListener('mousemove', function(e) {
            if (!isResizingTextarea) return;

            let deltaY = e.clientY - startY;
            let newHeight = startHeight + deltaY;
            let maxHeight = parseInt(dataRequest.style.maxHeight);

            if (newHeight >= 40 && newHeight <= maxHeight) {
                dataRequest.style.height = newHeight + 'px';
                updateIndicatorPosition();
            }
        });

        document.addEventListener('mouseup', function() {
            if (isResizingTextarea) {
                isResizingTextarea = false;
            }
        });
    }

    resizeDataResponse();
    window.addEventListener('resize', () => {
        if (dataRequest) {
            let actionAreaHeight = actionArea.offsetHeight;
            let maxHeight = actionAreaHeight - 200;
            dataRequest.style.maxHeight = maxHeight + 'px';
        }
        resizeDataResponse();
    });

    let resizeObserver = new ResizeObserver((entries) => {
        for (let entry of entries) {
            if (entry.target.tagName === 'TEXTAREA') {
                if (entry.target.id === 'data-request') {
                    let height = entry.target.style.height;
                    store.set('zato.data-request-height', height);
                    resizeDataResponse();
                }
            }
        }
    });

    let textareas = actionArea.querySelectorAll('textarea');
    textareas.forEach(ta => {
        resizeObserver.observe(ta);
    });

    $("#history-overlay-close").click($.fn.zato.ide.close_history_overlay);
    $(".history-overlay-backdrop").click($.fn.zato.ide.close_history_overlay);
    $("#history-search-input").on("input", function() {
        $.fn.zato.ide.filter_history_overlay($(this).val());
    });

    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            if (!$("#request-history-overlay").hasClass("hidden")) {
                e.preventDefault();
                $.fn.zato.ide.close_history_overlay();
            }
        }
    });
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.init_resizer = function() {
    console.log("init_resizer: START");

    let resizer = document.getElementById('resizer');
    let actionArea = document.getElementById('action-area-container');
    let container = document.getElementById('main-area-container');

    console.log("init_resizer: resizer element:", resizer);
    console.log("init_resizer: actionArea element:", actionArea);
    console.log("init_resizer: container element:", container);

    console.log("init_resizer: testing store write/read");
    store.set('zato.test-key', 'test-value');
    let testValue = store.get('zato.test-key');
    console.log("init_resizer: test value retrieved:", JSON.stringify(testValue));

    let savedWidth = store.get('zato.action-area-width');
    console.log("init_resizer: savedWidth from store:", JSON.stringify(savedWidth));
    console.log("init_resizer: localStorage.length:", localStorage.length);

    for (let i = 0; i < localStorage.length; i++) {
        let key = localStorage.key(i);
        console.log("init_resizer: localStorage key " + i + ":", key);
    }

    if (savedWidth) {
        console.log("init_resizer: setting actionArea width to:", savedWidth);
        actionArea.style.setProperty('width', savedWidth, 'important');
        console.log("init_resizer: actionArea.style.width after setting:", actionArea.style.width);
    } else {
        console.log("init_resizer: no saved width found, using default");
    }

    let isResizing = false;

    resizer.addEventListener('mousedown', function(e) {
        console.log("init_resizer: mousedown on resizer");
        isResizing = true;
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', function(e) {
        if (!isResizing) return;

        let containerRect = container.getBoundingClientRect();
        let newWidth = containerRect.right - e.clientX;

        console.log("init_resizer: mousemove - containerRect.right:", containerRect.right);
        console.log("init_resizer: mousemove - e.clientX:", e.clientX);
        console.log("init_resizer: mousemove - calculated newWidth:", newWidth);
        console.log("init_resizer: mousemove - containerRect.width:", containerRect.width);

        if (newWidth >= 200 && newWidth <= containerRect.width - 200) {
            actionArea.style.width = newWidth + 'px';
            console.log("init_resizer: mousemove - set width to:", newWidth + 'px');
        } else {
            console.log("init_resizer: mousemove - width out of bounds, not setting");
        }
    });

    document.addEventListener('mouseup', function() {
        if (isResizing) {
            console.log("init_resizer: mouseup - resizing ended");
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            let widthToSave = actionArea.style.width;
            console.log("init_resizer: mouseup - actionArea.style.width:", widthToSave);
            console.log("init_resizer: mouseup - saving to store with key 'zato.action-area-width'");
            store.set('zato.action-area-width', widthToSave);
            let verifyRead = store.get('zato.action-area-width');
            console.log("init_resizer: mouseup - immediately reading back from store:", JSON.stringify(verifyRead));
        }
    });

    console.log("init_resizer: END");
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
    let key = $.fn.zato.ide.get_current_source_code_key()
    let value = window.zato_editor.getValue();
    localStorage.setItem(key, value);
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.load_current_source_code_from_local_storage = function() {
    let key = $.fn.zato.ide.get_current_source_code_key()
    let value = localStorage.getItem(key)
    if(value) {
        window.zato_editor.setValue(value);
        window.zato_editor.clearSelection();
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

// Deploys the current file
$.fn.zato.ide.on_key_deploy_file = function(_ignored_event, _ignored_handler) {
    $.fn.zato.invoker.on_deploy_submitted();
}

// Invokes the current service
$.fn.zato.ide.on_key_invoke = function(_ignored_event, _ignored_handler) {
    $.fn.zato.invoker.on_invoke_submitted();
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
    after_on_file_op_success_func_callback,
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
        if(after_on_file_op_success_func_callback) {
            after_on_file_op_success_func_callback();
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
    let after_on_file_op_success_func_on_file_simple_impl = function() {
        $.fn.zato.ide.populate_current_file_service_list_impl(after_on_file_op_success_func_impl, "1");
    }

    let _on_success_func = $.fn.zato.ide.on_file_op_success_func(op_name, placeholder_verb, after_on_file_op_success_func_on_file_simple_impl);
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
    let after_on_file_op_success_func_on_file_delete_impl = function() {
        $.fn.zato.ide.populate_file_list($.fn.zato.ide.after_file_deleted);
        console.log(`Deleted "${fs_location}"`);
    }

    let url_path = "/zato/service/ide/delete-file/";
    let form_id = "file-delete-form";
    let options = {};
    let display_timeout = 1;
    let _on_success_func = $.fn.zato.ide.on_file_op_success_func("delete", "Deleting", after_on_file_op_success_func_on_file_delete_impl);
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

$.fn.zato.ide.postprocess_file_buttons = function(current_file_service_list) {
    // A list of buttons that depend on a file being selected.
    const file_buttons = ["#file-rename", "#file-delete", "#file-reload"];

    // Get the current file context
    const current_fs_location = $.fn.zato.ide.get_current_fs_location();

    // If no file is selected, disable all file-related buttons and the invoke button.
    if (!current_fs_location) {
        file_buttons.forEach(button_id => $.fn.zato.ide.disable_button(button_id));
        $.fn.zato.ide.disable_invoke_button();
        return; // Exit early
    }

    // If a file is selected, enable buttons by default, then apply specific disabling rules.
    file_buttons.forEach(button_id => $.fn.zato.ide.enable_button(button_id));

    // Rule: Disable rename/delete for services or demo.py
    const current_object_type = $.fn.zato.ide.get_current_object_type();
    const is_service_view = current_object_type === "service";
    const is_demo_file = current_fs_location.endsWith("demo.py");
    if (is_service_view || is_demo_file) {
        $.fn.zato.ide.disable_file_rename_button();
        $.fn.zato.ide.disable_file_delete_button();
    }

    // Rule: Handle the invoke button state.
    const is_service_file = current_file_service_list && current_file_service_list.length > 0;
    if (is_service_file) {
        // Always enable for services. The click handler deals with deployment.
        $.fn.zato.ide.enable_invoke_button();
    } else {
        $.fn.zato.ide.disable_invoke_button();
    }
};

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
    console.log("post_load_source_object: START");
    console.log("post_load_source_object: fs_location:", JSON.stringify(fs_location));
    console.log("post_load_source_object: current_file_source_code length:", current_file_source_code ? current_file_source_code.length : null);

    // First, establish the new baseline for deployment status. The content we just received from the server
    // is now considered the "last deployed" version for the purpose of detecting unsaved changes.
    let key = $.fn.zato.ide.get_last_deployed_key();
    console.log("post_load_source_object: setting baseline with key:", JSON.stringify(key));
    localStorage.setItem(key, current_file_source_code);
    console.log("post_load_source_object: baseline set in localStorage");

    // Now, load the content into the editor. Any subsequent 'change' event will compare against the correct baseline.
    $.fn.zato.ide.load_editor_session(fs_location, current_file_source_code, reuse_source_code);

    $.fn.zato.ide.highlight_current_file(fs_location);
    if(get_current_file_service_list_func) {
        current_file_service_list = get_current_file_service_list_func();
    }
    $.fn.zato.ide.populate_current_file_service_list(current_file_service_list, object_name);

    // Check the actual deployment status by comparing editor content against baseline
    console.log("post_load_source_object: checking deployment status");
    $.fn.zato.ide.set_deployment_status();
    console.log("post_load_source_object: END");

    $.fn.zato.ide.set_is_current_file(fs_location);
    if(after_post_load_source_func) {
        after_post_load_source_func(data);
    }

    // This will enable or disable file buttons
    $.fn.zato.ide.postprocess_file_buttons(current_file_service_list);
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

    console.log("load_source_object: START");
    console.log("load_source_object: object_type:", JSON.stringify(object_type));
    console.log("load_source_object: object_name:", JSON.stringify(object_name));
    console.log("load_source_object: fs_location:", JSON.stringify(fs_location));

    extra_qs = extra_qs || "";

    var callback = function(data, _unused_status) {
        console.log("load_source_object: callback START");
        let msg = data.responseText;
        console.log("load_source_object: msg length:", msg ? msg.length : null);
        let json = JSON.parse(msg)
        console.log("load_source_object: json parsed");
        let current_file_source_code = json.current_file_source_code;
        console.log("load_source_object: current_file_source_code length:", current_file_source_code ? current_file_source_code.length : null);
        console.log("load_source_object: current_file_source_code type:", typeof current_file_source_code);
        console.log("load_source_object: current_file_source_code:", JSON.stringify(current_file_source_code));
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

$.fn.zato.ide.load_editor_session = function(fs_location, source_code, reuse_source_code) {

    console.log(`ZATO_IDE_DEBUG: load_editor_session called for fs_location: ${fs_location}`);
    console.log(`ZATO_IDE_DEBUG: load_editor_session received source_code:`, JSON.stringify(source_code));
    console.log(`ZATO_IDE_DEBUG: load_editor_session reuse_source_code:`, reuse_source_code);

    // Do we have a session for this file already?
    let existing_session = window.zato_editor_session_map[fs_location];

    // If we have an existing session and should reuse it, switch to it
    if(existing_session && reuse_source_code) {
        console.log(`ZATO_IDE_DEBUG: Reusing existing session for ${fs_location}, keeping existing content.`);
        window.zato_editor.setSession(existing_session);
    }
    // If we should not reuse or don't have a session, create/replace with server content
    else {
        console.log(`ZATO_IDE_DEBUG: Creating new session for ${fs_location} with server source code.`);
        let new_session = ace.createEditSession(source_code);
        $.fn.zato.ide.set_up_editor_session(new_session);
        window.zato_editor.setSession(new_session);
        window.zato_editor_session_map[fs_location] = new_session;
    }

    // Set mode depending on file name
    if(fs_location.endsWith(".py")) {
        window.zato_editor.session.setMode("ace/mode/python");
    }
    else if(fs_location.endsWith(".json")) {
        window.zato_editor.session.setMode("ace/mode/json");
    }
    else {
        window.zato_editor.session.setMode("ace/mode/text");
    }
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.save_current_editor_session = function() {
    let current_fs_location = $.fn.zato.ide.get_current_fs_location();
    let session = window.zato_editor.getSession();
    console.log(`ZATO_IDE_DEBUG: save_current_editor_session for ${current_fs_location}`);
    console.log(`ZATO_IDE_DEBUG: session content length:`, session.getValue().length);
    window.zato_editor_session_map[current_fs_location] = session;
    console.log(`ZATO_IDE_DEBUG: session map keys:`, Object.keys(window.zato_editor_session_map));
}

/* ---------------------------------------------------------------------------------------------------------------------------- */

$.fn.zato.ide.get_last_deployed_from_store = function(key) {
    let last_deployed = localStorage.getItem(key);
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
        localStorage.setItem(key, editor_value);
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
    console.log("on_editor_changed: START");
    $.fn.zato.ide.set_deployment_status();
    console.log("on_editor_changed: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.set_deployment_status = function() {
    console.log("set_deployment_status: START");

    // Get the current value of the editor ..
    let editor_value = window.zato_editor.getValue()
    console.log("set_deployment_status: editor_value length:", editor_value ? editor_value.length : null);
    console.log("set_deployment_status: editor_value:", JSON.stringify(editor_value));

    // .. get the value of what was last deployed ..
    let key = $.fn.zato.ide.get_last_deployed_key();
    console.log("set_deployment_status: key:", JSON.stringify(key));

    let last_deployed = $.fn.zato.ide.get_last_deployed_from_store(key);
    console.log("set_deployment_status: last_deployed length:", last_deployed ? last_deployed.length : null);
    console.log("set_deployment_status: last_deployed:", JSON.stringify(last_deployed));

    // .. check if they are different ..
    let is_different = editor_value != last_deployed;
    console.log("set_deployment_status: is_different:", is_different);

    // .. pick the correct CSS class to set for the "Deploy" button
    if(is_different) {
        var button_class_name = "different";
        console.log("set_deployment_status: setting button_class_name to 'different'");
    }
    else {
        var button_class_name = "not-different";
        console.log("set_deployment_status: setting button_class_name to 'not-different'");
    }

    // .. set it for the button accordingly ..
    $.fn.zato.ide.set_deployment_button_status_class(button_class_name);

    // .. and for all the select options that point to the current file ..
    $.fn.zato.ide.update_deployment_option_state(is_different);

    // .. update the document title to add or remove the star ..
    let title = document.title;
    console.log("set_deployment_status: current title:", JSON.stringify(title));
    console.log("set_deployment_status: title starts with '* ':", title.startsWith('* '));
    if(is_different) {
        if(!title.startsWith('* ')) {
            document.title = '* ' + title;
            console.log("set_deployment_status: added star to title");
        }
    } else {
        if(title.startsWith('* ')) {
            document.title = title.substring(2);
            console.log("set_deployment_status: removed star from title");
        } else {
            console.log("set_deployment_status: title does not start with '* ', not removing");
        }
    }

    console.log("set_deployment_status: END");
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
    $.fn.zato.ide.set_deployment_status();
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
    localStorage.setItem(key, editor_value);

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
        console.log("post_populate_current_file_service_list_impl: response:", JSON.stringify(response));
        let data = JSON.parse(response.responseText);
        console.log("post_populate_current_file_service_list_impl: data.current_file_service_list:", JSON.stringify(data.current_file_service_list));
        console.log("post_populate_current_file_service_list_impl: data.current_fs_location:", JSON.stringify(data.current_fs_location));
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

    console.log("populate_current_file_service_list_impl: url_path:", JSON.stringify(url_path));
    console.log("populate_current_file_service_list_impl: current_fs_location:", JSON.stringify(current_fs_location));
    console.log("populate_current_file_service_list_impl: should_wait_for_services:", JSON.stringify(should_wait_for_services));

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

$.fn.zato.ide.get_request_history_key = function() {
    let cluster_name = $.fn.zato.ide.get_cluster_name();
    let key = window.zato_local_storage_key.zato_request_history + "." + cluster_name;
    return key;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_request_history = function() {
    let key = $.fn.zato.ide.get_request_history_key();
    let history_json = localStorage.getItem(key);
    if (history_json) {
        return JSON.parse(history_json);
    }
    return [];
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.update_request_history_buttons = function() {
    console.log("update_request_history_buttons: START");

    let history = $.fn.zato.ide.get_request_history();
    let history_length = history.length;
    let current_index = window.zato_request_history_index;

    console.log("update_request_history_buttons: history_length:", history_length);
    console.log("update_request_history_buttons: current_index:", current_index);

    let up_button = $("#request-history-up");
    let down_button = $("#request-history-down");

    if (history_length === 0) {
        console.log("update_request_history_buttons: history is empty, disabling both buttons");
        $.fn.zato.ide.disable_button("#request-history-up");
        $.fn.zato.ide.disable_button("#request-history-down");
    } else {
        if (current_index < history_length - 1) {
            console.log("update_request_history_buttons: enabling up button");
            $.fn.zato.ide.enable_button("#request-history-up");
        } else {
            console.log("update_request_history_buttons: disabling up button");
            $.fn.zato.ide.disable_button("#request-history-up");
        }

        if (current_index > 0) {
            console.log("update_request_history_buttons: enabling down button (current_index > 0)");
            $.fn.zato.ide.enable_button("#request-history-down");
        } else if (current_index === 0) {
            console.log("update_request_history_buttons: enabling down button (current_index === 0)");
            $.fn.zato.ide.enable_button("#request-history-down");
        } else {
            console.log("update_request_history_buttons: disabling down button");
            $.fn.zato.ide.disable_button("#request-history-down");
        }
    }

    console.log("update_request_history_buttons: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_full_history_key = function() {
    let cluster_name = $.fn.zato.ide.get_cluster_name();
    let key = window.zato_local_storage_key.zato_full_history + "." + cluster_name;
    return key;
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.get_full_history = function() {
    let key = $.fn.zato.ide.get_full_history_key();
    let history_json = localStorage.getItem(key);
    if (history_json) {
        return JSON.parse(history_json);
    }
    return [];
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.save_request_to_history = function(request_text, response_text) {
    console.log("save_request_to_history: START");
    console.log("save_request_to_history: request_text:", JSON.stringify(request_text));
    console.log("save_request_to_history: request_text.length:", request_text ? request_text.length : 0);
    console.log("save_request_to_history: response_text:", JSON.stringify(response_text));

    if (!request_text) {
        request_text = '';
    }

    let key = $.fn.zato.ide.get_request_history_key();
    console.log("save_request_to_history: key:", JSON.stringify(key));

    let history = $.fn.zato.ide.get_request_history();
    console.log("save_request_to_history: history before save:", JSON.stringify(history));
    console.log("save_request_to_history: history.length before save:", history.length);

    if (history.length > 0) {
        let first_text = typeof history[0] === 'string' ? history[0] : history[0].text;
        if (first_text === request_text) {
            console.log("save_request_to_history: request_text is same as history[0], updating timestamp and response");
            if (typeof history[0] === 'object') {
                history[0].timestamp = Date.now();
                history[0].response = response_text || '';
                localStorage.setItem(key, JSON.stringify(history));
            }

            let full_history_key = $.fn.zato.ide.get_full_history_key();
            let full_history = $.fn.zato.ide.get_full_history();
            if (full_history.length > 0 && typeof full_history[0] === 'object') {
                let full_first_text = full_history[0].text;
                if (full_first_text === request_text) {
                    full_history[0].timestamp = Date.now();
                    full_history[0].response = response_text || '';
                    localStorage.setItem(full_history_key, JSON.stringify(full_history));
                }
            }

            $.fn.zato.ide.update_request_history_buttons();
            $.fn.zato.ide.populate_history_overlay();
            return;
        }
    }

    console.log("save_request_to_history: removing duplicates of request_text from history");
    history = history.filter(function(item) {
        let text = typeof item === 'string' ? item : item.text;
        return text !== request_text;
    });
    console.log("save_request_to_history: history after removing duplicates:", JSON.stringify(history));

    console.log("save_request_to_history: adding request_text to history");
    let entry = {
        text: request_text,
        response: response_text || '',
        timestamp: Date.now()
    };
    history.unshift(entry);
    console.log("save_request_to_history: history after unshift:", JSON.stringify(history));
    console.log("save_request_to_history: history.length after unshift:", history.length);

    const max_history_size = 100;
    if (history.length > max_history_size) {
        console.log("save_request_to_history: trimming history to max_history_size:", max_history_size);
        history = history.slice(0, max_history_size);
    }

    console.log("save_request_to_history: saving to localStorage");
    localStorage.setItem(key, JSON.stringify(history));

    console.log("save_request_to_history: resetting index to -1");
    window.zato_request_history_index = -1;
    console.log("save_request_to_history: window.zato_request_history_index:", window.zato_request_history_index);

    $.fn.zato.ide.update_request_history_buttons();
    console.log("save_request_to_history: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_request_history_up = function() {
    console.log("on_request_history_up: START");

    let current_textarea_value = $("#data-request").val();
    console.log("on_request_history_up: current textarea value:", JSON.stringify(current_textarea_value));

    let history = $.fn.zato.ide.get_request_history();
    console.log("on_request_history_up: history:", JSON.stringify(history));
    console.log("on_request_history_up: history.length:", history.length);

    if (history.length === 0) {
        console.log("on_request_history_up: history is empty, returning");
        return;
    }

    let current_index = window.zato_request_history_index;
    console.log("on_request_history_up: current_index:", current_index);

    let new_index = current_index + 1;
    console.log("on_request_history_up: new_index (before adjustment):", new_index);

    if (current_index === -1 && history.length > 0) {
        let first_text = typeof history[0] === 'string' ? history[0] : history[0].text;
        if (current_textarea_value === first_text) {
            console.log("on_request_history_up: at index -1 and textarea matches history[0], skipping to index 1");
            new_index = 1;
        }
    }

    console.log("on_request_history_up: new_index (after adjustment):", new_index);

    if (new_index >= history.length) {
        console.log("on_request_history_up: new_index >= history.length, returning");
        return;
    }

    console.log("on_request_history_up: setting window.zato_request_history_index to:", new_index);
    window.zato_request_history_index = new_index;

    let item = history[new_index];
    let request_text = typeof item === 'string' ? item : item.text;
    console.log("on_request_history_up: request_text from history[" + new_index + "]:", JSON.stringify(request_text));

    console.log("on_request_history_up: setting textarea value");
    $("#data-request").val(request_text);
    console.log("on_request_history_up: textarea value after set:", JSON.stringify($("#data-request").val()));

    $.fn.zato.ide.update_request_history_buttons();
    console.log("on_request_history_up: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_request_history_down = function() {
    console.log("on_request_history_down: START");
    console.log("on_request_history_down: current textarea value:", JSON.stringify($("#data-request").val()));

    let history = $.fn.zato.ide.get_request_history();
    console.log("on_request_history_down: history:", JSON.stringify(history));
    console.log("on_request_history_down: history.length:", history.length);

    if (history.length === 0) {
        console.log("on_request_history_down: history is empty, returning");
        return;
    }

    let current_index = window.zato_request_history_index;
    console.log("on_request_history_down: current_index:", current_index);

    let new_index = current_index - 1;
    console.log("on_request_history_down: new_index:", new_index);

    if (new_index < -1) {
        console.log("on_request_history_down: new_index < -1, returning");
        return;
    }

    console.log("on_request_history_down: setting window.zato_request_history_index to:", new_index);
    window.zato_request_history_index = new_index;

    if (new_index === -1) {
        console.log("on_request_history_down: new_index is -1, clearing textarea");
        $("#data-request").val("");
    } else {
        let item = history[new_index];
        let request_text = typeof item === 'string' ? item : item.text;
        console.log("on_request_history_down: request_text from history[" + new_index + "]:", JSON.stringify(request_text));
        console.log("on_request_history_down: setting textarea value");
        $("#data-request").val(request_text);
    }

    console.log("on_request_history_down: textarea value after set:", JSON.stringify($("#data-request").val()));

    $.fn.zato.ide.update_request_history_buttons();
    console.log("on_request_history_down: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.open_history_overlay = function() {
    console.log("open_history_overlay: START");

    let overlay = $("#request-history-overlay");
    let history = $.fn.zato.ide.get_request_history();

    console.log("open_history_overlay: history:", JSON.stringify(history));

    $.fn.zato.ide.populate_history_overlay(history);

    overlay.removeClass("hidden");

    $("#history-search-input").val("");
    $("#history-search-input").focus();

    $.fn.zato.ide.init_history_overlay_drag();

    console.log("open_history_overlay: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.init_history_overlay_drag = function() {
    let content = document.querySelector(".history-overlay-content");
    let header = document.querySelector(".history-overlay-header");

    if (!content || !header || header.dataset.dragInitialized) {
        return;
    }

    header.dataset.dragInitialized = "true";
    header.style.cursor = "move";

    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;

    header.addEventListener("mousedown", function(e) {
        if (e.target.closest(".history-close-btn")) {
            return;
        }

        isDragging = true;

        let rect = content.getBoundingClientRect();
        initialX = e.clientX - rect.left;
        initialY = e.clientY - rect.top;

        content.style.position = "fixed";
        content.style.margin = "0";
    });

    document.addEventListener("mousemove", function(e) {
        if (!isDragging) return;

        e.preventDefault();

        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;

        content.style.left = currentX + "px";
        content.style.top = currentY + "px";
    });

    document.addEventListener("mouseup", function() {
        isDragging = false;
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.close_history_overlay = function() {
    console.log("close_history_overlay: called");
    $("#request-history-overlay").addClass("hidden");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.format_timestamp = function(timestamp) {
    let now = new Date();
    let then = new Date(timestamp);
    let diffMs = now - then;
    let diffSec = Math.floor(diffMs / 1000);
    let diffMin = Math.floor(diffSec / 60);
    let diffHour = Math.floor(diffMin / 60);
    let diffDay = Math.floor(diffHour / 24);

    let timeStr = then.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });

    if (diffSec < 60) {
        if (diffSec === 0) diffSec = 1;
        return diffSec === 1 ? '1 second ago' : diffSec + ' seconds ago';
    } else if (diffMin < 60) {
        return diffMin === 1 ? '1 minute ago' : diffMin + ' minutes ago';
    } else if (diffHour < 24) {
        return diffHour === 1 ? '1 hour ago' : diffHour + ' hours ago';
    } else if (diffDay === 1) {
        return 'yesterday at ' + timeStr;
    } else if (diffDay < 7) {
        return diffDay + ' days ago at ' + timeStr;
    } else if (diffDay < 14) {
        let dayName = then.toLocaleDateString('en-US', { weekday: 'long' });
        return dayName + ', last week at ' + timeStr;
    } else if (diffDay < 21) {
        let dayName = then.toLocaleDateString('en-US', { weekday: 'long' });
        return dayName + ', two weeks ago at ' + timeStr;
    } else if (diffDay < 60) {
        return 'a month ago at ' + timeStr;
    } else if (diffDay < 365) {
        let months = Math.floor(diffDay / 30);
        return months === 1 ? 'a month ago at ' + timeStr : months + ' months ago at ' + timeStr;
    } else {
        let years = Math.floor(diffDay / 365);
        return years === 1 ? 'a year ago at ' + timeStr : years + ' years ago at ' + timeStr;
    }
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.populate_history_overlay = function(history, is_search_result) {
    console.log("populate_history_overlay: START");

    if (!history) {
        history = $.fn.zato.ide.get_full_history();
    }

    console.log("populate_history_overlay: history.length:", history.length);
    console.log("populate_history_overlay: is_search_result:", is_search_result);

    let list_container = $("#history-overlay-list");
    list_container.empty();

    if (history.length === 0) {
        let message = is_search_result ? 'No results' : 'Nothing in history';
        list_container.append('<div class="history-empty">' + message + '</div>');
        return;
    }

    for (let i = 0; i < history.length; i++) {
        let item = history[i];
        let request_text = typeof item === 'string' ? item : item.text;
        let timestamp = typeof item === 'string' ? null : item.timestamp;
        let response = typeof item === 'string' ? '' : (item.response || '');

        let has_response = response && response.trim() !== '' && response.trim() !== 'None' && response.trim() !== '(None)';

        let wrapper = $('<div class="history-item-wrapper"></div>');
        let number_box = $('<div class="history-item-number"></div>');
        number_box.text((i + 1));
        let text_box = $('<div class="history-item-text"></div>');
        text_box.text(request_text && request_text.trim() !== '' ? request_text : '(No request)');

        let show_response_box = $('<div class="history-item-show-response"></div>');
        show_response_box.text(has_response ? "Show response" : "(No response)");

        let timestamp_box = $('<div class="history-item-timestamp"></div>');
        if (timestamp) {
            timestamp_box.text($.fn.zato.ide.format_timestamp(timestamp));
        } else {
            timestamp_box.text('');
        }

        let delete_box = $('<div class="history-item-delete"></div>');
        delete_box.text("✕");

        text_box.on("click", function() {
            $.fn.zato.ide.on_history_item_selected($(this).parent().attr("data-index"));
        });

        number_box.on("click", function() {
            $.fn.zato.ide.on_history_item_selected($(this).parent().attr("data-index"));
        });

        timestamp_box.on("click", function() {
            $.fn.zato.ide.on_history_item_selected($(this).parent().attr("data-index"));
        });

        show_response_box.on("click", function(e) {
            e.stopPropagation();
            let wrapper = $(this).parent();
            let detail_id = "history-response-detail-" + i;
            let existing_detail = $("#" + detail_id);

            if (existing_detail.length > 0) {
                existing_detail.toggleClass("visible");
            } else {
                let response = typeof item === 'string' ? '' : (item.response || '');
                let detail = $('<div class="history-response-detail visible" id="' + detail_id + '"></div>');

                let header = $('<div class="history-response-detail-header"></div>');
                let title = $('<div class="history-response-detail-title">Response</div>');
                let copy_btn_id = "history-response-copy-" + i;
                let copy_btn = $('<button class="history-response-detail-copy" id="' + copy_btn_id + '">Copy</button>');

                copy_btn.on("click", function(e) {
                    console.log("copy_btn clicked: START, id:", copy_btn_id);
                    e.stopPropagation();
                    console.log("copy_btn: event.stopPropagation called");
                    console.log("copy_btn: response length:", response.length);

                    if (!response || response.trim() === '' || response.trim() === 'None' || response.trim() === '(None)') {
                        console.log("copy_btn: response is empty, showing nothing to copy message");
                        let tippy_root_before = $("[data-tippy-root]");
                        tippy_root_before.each(function(idx, elem) {
                            $(elem).css("z-index", "10001");
                        });

                        let copy_btn_elem = $("#" + copy_btn_id);

                        let error_tooltip = tippy("#" + copy_btn_id, {
                            content: '<span style="color: #ff6666;">Nothing to copy</span>',
                            allowHTML: true,
                            theme: "dark",
                            trigger: "manual",
                            placement: "bottom",
                            arrow: true,
                            interactive: false,
                            inertia: true,
                            role: "tooltip",
                        });

                        if (error_tooltip) {
                            error_tooltip[0].show();
                        }

                        setTimeout(function() {
                            let tippy_root = $("[data-tippy-root]");
                            tippy_root.each(function(idx, elem) {
                                $(elem).css("z-index", "10001");
                            });
                        }, 10);

                        setTimeout(function() {
                            if (error_tooltip) {
                                error_tooltip[0].hide();
                            }
                        }, Copy_Tooltip_Timeout);
                        return;
                    }

                    console.log("copy_btn: about to call navigator.clipboard.writeText");

                    navigator.clipboard.writeText(response).then(function() {
                        console.log("copy_btn: clipboard.writeText SUCCESS");
                        console.log("copy_btn: about to call $.fn.zato.show_bottom_tooltip");
                        console.log("copy_btn: selector:", "#" + copy_btn_id);
                        console.log("copy_btn: message:", "Response copied to clipboard");

                        let tooltip_elem = $("#" + copy_btn_id);
                        console.log("copy_btn: tooltip_elem found:", tooltip_elem.length);
                        console.log("copy_btn: tooltip_elem offset:", tooltip_elem.offset());
                        console.log("copy_btn: tooltip_elem css position:", tooltip_elem.css("position"));
                        console.log("copy_btn: tooltip_elem css z-index:", tooltip_elem.css("z-index"));

                        let tippy_root_before = $("[data-tippy-root]");
                        console.log("copy_btn: BEFORE show_bottom_tooltip - tippy_root elements found:", tippy_root_before.length);
                        tippy_root_before.each(function(idx, elem) {
                            let $elem = $(elem);
                            console.log("copy_btn: BEFORE - tippy_root[" + idx + "] z-index:", $elem.css("z-index"));
                            $elem.css("z-index", "10001");
                            console.log("copy_btn: BEFORE - tippy_root[" + idx + "] z-index set to 10001");
                        });

                        $.fn.zato.show_bottom_tooltip("#" + copy_btn_id, "Response copied to clipboard");
                        console.log("copy_btn: $.fn.zato.show_bottom_tooltip CALLED");

                        setTimeout(function() {
                            let tippy_root = $("[data-tippy-root]");
                            console.log("copy_btn: AFTER timeout - tippy_root elements found:", tippy_root.length);
                            tippy_root.each(function(idx, elem) {
                                let $elem = $(elem);
                                console.log("copy_btn: AFTER - tippy_root[" + idx + "] z-index:", $elem.css("z-index"));
                                $elem.css("z-index", "10001");
                                console.log("copy_btn: AFTER - tippy_root[" + idx + "] z-index set to 10001");
                            });

                            let overlay = $(".history-overlay");
                            console.log("copy_btn: overlay z-index:", overlay.css("z-index"));
                            console.log("copy_btn: overlay display:", overlay.css("display"));
                        }, 10);

                        setTimeout(function() {
                            let copy_btn_elem = $("#" + copy_btn_id);
                            let tooltip_instance = copy_btn_elem[0]._tippy;
                            if (tooltip_instance) {
                                tooltip_instance.hide();
                            }
                        }, Copy_Tooltip_Timeout);

                        console.log("copy_btn: END");
                    }).catch(function(err) {
                        console.log("copy_btn: clipboard.writeText FAILED:", err);
                    });
                });

                header.append(title);
                header.append(copy_btn);

                let content = $('<div class="history-response-detail-content"></div>');
                if (!response || response.trim() === '' || response.trim() === 'None' || response.trim() === '(None)') {
                    content.text('(No response)');
                } else {
                    content.text(response);
                }

                detail.append(header);
                detail.append(content);

                wrapper.after(detail);
            }
        });

        delete_box.on("click", function(e) {
            e.stopPropagation();
            $.fn.zato.ide.on_history_item_delete($(this).parent().attr("data-index"));
        });

        wrapper.append(number_box);
        wrapper.append(text_box);
        wrapper.append(show_response_box);
        wrapper.append(timestamp_box);
        wrapper.append(delete_box);
        wrapper.attr("data-index", i);
        list_container.append(wrapper);
    }

    console.log("populate_history_overlay: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_history_item_selected = function(index) {
    console.log("on_history_item_selected: index:", index);

    let history = $.fn.zato.ide.get_request_history();
    let item = history[index];
    let request_text = typeof item === 'string' ? item : item.text;

    console.log("on_history_item_selected: request_text:", JSON.stringify(request_text));

    $("#data-request").val(request_text);

    window.zato_request_history_index = parseInt(index);
    console.log("on_history_item_selected: set window.zato_request_history_index to:", window.zato_request_history_index);

    $.fn.zato.ide.close_history_overlay();
    $.fn.zato.ide.update_request_history_buttons();

    $("#data-request").focus();

    console.log("on_history_item_selected: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.filter_history_overlay = function(search_text) {
    console.log("filter_history_overlay: search_text:", JSON.stringify(search_text));

    let history = $.fn.zato.ide.get_request_history();
    let filtered = history;
    let is_search_result = false;

    if (history.length === 0) {
        $.fn.zato.ide.populate_history_overlay(filtered, false);
        return;
    }

    if (search_text && search_text.trim() !== "") {
        filtered = history.filter(function(item) {
            let text = typeof item === 'string' ? item : item.text;
            return text.toLowerCase().indexOf(search_text.toLowerCase()) !== -1;
        });
        is_search_result = true;
    }

    $.fn.zato.ide.populate_history_overlay(filtered, is_search_result);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.ide.on_history_item_delete = function(index) {
    console.log("on_history_item_delete: index:", index);

    let history = $.fn.zato.ide.get_request_history();
    history.splice(index, 1);

    let key = $.fn.zato.ide.get_request_history_key();
    localStorage.setItem(key, JSON.stringify(history));

    $.fn.zato.ide.populate_history_overlay(history);
    $.fn.zato.ide.update_request_history_buttons();

    console.log("on_history_item_delete: END");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
