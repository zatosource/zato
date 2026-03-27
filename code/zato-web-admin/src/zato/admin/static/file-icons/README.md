File Icons
==========

This is the source for the [File Icons][1] project's custom icon-font.

Please [submit a request][2] if an icon is missing.

[1]: https://github.com/file-icons/atom
[2]: https://github.com/file-icons/icons/issues/new


“Why request an icon? Can't I submit a PR?”
--------------------------------------------------------------------------------
You can. But your submission will end up getting overwritten.

Everything in the [`svg`](./svg) directory is meticulously optimised by hand, so
that each icon contains as few control-points as possible:

![Icon optimisation example, taken from DevOpicons readme](https://git.io/JUohT)

This task requires time, patience, and above-average aptitude with image editing
software. Even if you have all three, I still have to check the SVG file myself;
both our lives are made easier by simply linking to where the icon can be found.
Failing that, you can use a [fenced code-block][3] to embed the SVG in the issue
itself:

[3]: https://docs.github.com/articles/creating-and-highlighting-code-blocks

<a name="template"></a>
~~~markdown
<details>

```svg
<!-- Replace this with the contents of your SVG file. -->
```

</details>
~~~

__Note:__
The empty line separating `<details>` from its content is required. Refer to the
[CommonMark spec](https://spec.commonmark.org/current/#html-blocks) for the gory
details of HTML handling in Markdown.
