# simplehtml2rst change log

# 1.1.0 (not yet released)

- Real `<blockquote>` handling.
- Handle html snippet by wrapping in `<body>` if not there already, to allow,
  e.g.:

        markdown2 foo.md | simplehtml2rst > foo.rst

- [issue #6] Just use inline link hrefs instead of pulling out to
  link refs at the bottom. The block of link refs at the bottom was
  predicated on "same link text" == "same href", which is wrong.
  Also have the URL at the link site is, IMO, more readable and
  true to the HTML input.
- [issue #1] Don't blow up on `<tbody>` or `<thead>`.
- [issue #2] Fix `<li><p>...` case where the bullet would get dropped.
- [issue #4] Don't drop internal links (i.e. to `#my-anchor` in the same doc).
- [issue #3] fix `<code>` handling
- Add CLI options: -h/--help, -v/--verbose, --version, etc.


# 1.0.0

A copy of "xhtml2rest.py" Revision: 3753 from
<http://sourceforge.net/p/docutils/code/HEAD/tree/trunk/sandbox/xhtml2rest/>.
