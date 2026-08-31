Vendored from [Prism.js](https://prismjs.com) 1.30.0 (MIT License, © 2012 Lea Verou).

Components: core, markup-templating, markup, clike, django, css, javascript,
python, bash — the language grammars this docs site's code examples need.
`markup-templating` + `django` is what lets a code block written as HTML with
embedded `{% %}`/`{{ }}` Django template tags highlight both correctly in one
pass (`language-django` on the `<code>` element).

Used only by the demo/docs site to syntax-highlight its own code examples —
not part of the design system's own component layer, and not loaded by a
project consuming `wise_core`/`wise_autocomplete`/`wise_richtext` directly.

To upgrade: `npm install prismjs@<version>` somewhere scratch, then copy the
same `prism-*.min.js` files from `node_modules/prismjs/components/` here.
