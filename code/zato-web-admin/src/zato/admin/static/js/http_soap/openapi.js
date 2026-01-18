
/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.init = function() {

    let openapi_import_content = `
        <input type="button" id="openapi-from-copy-paste" value="From copy/paste" onclick="$.fn.zato.http_soap.openapi.on_from_copy_paste();"/>
        <input type="button" id="openapi-from-url" value="From URL" onclick="$.fn.zato.http_soap.openapi.on_from_url();"/>
    `;

    tippy("#openapi-import-link", {
        content: openapi_import_content,
        allowHTML: true,
        theme: "light",
        trigger: "click",
        placement: "bottom",
        arrow: true,
        interactive: true,
    });

    $("#openapi-copy-paste-close").click($.fn.zato.http_soap.openapi.close_copy_paste_overlay);
    $("#openapi-copy-paste-cancel").click($.fn.zato.http_soap.openapi.close_copy_paste_overlay);
    $("#openapi-copy-paste-ok").click($.fn.zato.http_soap.openapi.on_copy_paste_ok);
    $(".openapi-overlay-backdrop").click($.fn.zato.http_soap.openapi.close_copy_paste_overlay);

    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            if (!$("#openapi-copy-paste-overlay").hasClass("hidden")) {
                e.preventDefault();
                $.fn.zato.http_soap.openapi.close_copy_paste_overlay();
            }
        }
    });

    $.fn.zato.http_soap.openapi.init_draggable();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.init_draggable = function() {
    let overlay_content = document.querySelector("#openapi-copy-paste-overlay .openapi-overlay-content");
    let header = document.querySelector("#openapi-copy-paste-overlay .openapi-overlay-header");

    if (!overlay_content || !header) {
        return;
    }

    let is_dragging = false;
    let offset_x = 0;
    let offset_y = 0;

    header.addEventListener("mousedown", function(e) {
        if (e.target.classList.contains("openapi-close-button")) {
            return;
        }
        is_dragging = true;
        offset_x = e.clientX - overlay_content.offsetLeft;
        offset_y = e.clientY - overlay_content.offsetTop;
        overlay_content.style.position = "absolute";
        overlay_content.style.margin = "0";
    });

    document.addEventListener("mousemove", function(e) {
        if (!is_dragging) {
            return;
        }
        let new_x = e.clientX - offset_x;
        let new_y = e.clientY - offset_y;
        overlay_content.style.left = new_x + "px";
        overlay_content.style.top = new_y + "px";
    });

    document.addEventListener("mouseup", function() {
        is_dragging = false;
    });
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_from_copy_paste = function() {
    $("#openapi-copy-paste-overlay").removeClass("hidden");
    $("#openapi-copy-paste-textarea").focus();
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_from_url = function() {
    alert("From URL clicked");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.close_copy_paste_overlay = function() {
    $("#openapi-copy-paste-overlay").addClass("hidden");
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

$.fn.zato.http_soap.openapi.on_copy_paste_ok = function() {
    let content = $("#openapi-copy-paste-textarea").val();
    alert("OK clicked. Content length: " + content.length);
}

/* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */
