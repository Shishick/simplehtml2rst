A pure Python module/script to convert simple HTML to reStructuredText.

"Simple" because this tool currently (and probably only ever) will support
dealing with fairly simple HTML. See my [ulterior motive](#ulterior-motive)
for why this is sufficient for my needs: Markdown conversion (modulo
embedded HTML) typically results in fairly simple HTML.

Thanks very much to Antonios Christofides (and Lea Wiemann) who wrote (and
maintained) the "xhtml2rest.py" script on which this module is based. See the
License section below for a link.


# Usage

    python simplehtml2rst.py foo.html > foo.rst


# Limitations

- Only *X*HTML input is supported -- at least currently. That's a heritage of
  the "xhtml2rest.py" original source of this module.

- No comprehensive test suite, so I'm sure there are rough edges.

- I'm currently using Python 2. However I'd be happy to support Python 3.
  Patches very welcome.

And a number of limitations from the original author (edited by me):

- No indented tables

- No multi-col or -row spans in tables

- No support for `<br>`

- Not tested in nested tables

- `<th>` support is quick and dirty

- If the same anchor text is met twice, the anchor is ignored

- No indented `<pre>` elements

- Images are ignored

- The word HARDWIRED in the code indicates a hardwired hack which is
  specific to the job I wanted ``xhtml2rest`` to do.



# License

MIT. See LICENSE.txt.

This module started with [the "xhtml2rest.py" script in the docutils svn
repository](http://sourceforge.net/p/docutils/code/HEAD/tree/trunk/sandbox/xhtml2rest/).
The original author is Antonios Christofides. I started with Revision 3753.
A header comment in the module placed it in the public domain.


# Ulterior Motive

I'm exploring a way to use [Sphinx](http://sphinx-doc.org/) with Markdown
instead of reStructuredText (aka RST). The basic plan is:

    markdown -> html -> rst

The idea is that HTML is the lingua franca here, such that this converter
shouldn't ever need to know about the various custom Markdown syntax
extensions.

The wildcard is reStructuredText/Sphinx directives such as `.. toctree::`.
Possibilities to handle that in this tool:

- some pragma-type support,
- support uncommenting reStructuredText directives embedded in the
  source Markdown (and hence the HTML) hidden in HTML comments,
- punt,
- something else

See <http://stackoverflow.com/a/2487862/122384> for other suggestions for
supporting Markdown in Sphinx.
