import js

def create_element():
    demo_container = js.document.getElementById("pyodide-demo-container")
    demo_element = js.document.createElement("div")
    demo_element.innerHTML = "DOM Manipulation from pyodide"
    demo_container.append(demo_element)
    jq = getattr(js, "$")
    jq("#pyodide-demo-container").append("<div>jQuery from pyodide</div>")