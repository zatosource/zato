from foo import bar, baz, js

print("hello from inside pyodide")
bar.hello_bar()
baz.hello_baz()
js.create_element()