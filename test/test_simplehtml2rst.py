#!/usr/bin/env python

"""Test simplehtml2rst.py."""

import os
import sys
from os.path import join, dirname, abspath, exists, splitext, basename
import re
from glob import glob
from pprint import pprint
import unittest
import codecs
import difflib
import doctest

from testlib import TestError, TestSkipped, tag

sys.path.insert(0, join(dirname(dirname(abspath(__file__)))))
try:
    import simplehtml2rst
finally:
    del sys.path[0]



#---- Python version compat

# Use `bytes` for byte strings and `unicode` for unicode strings (str in Py3).
if sys.version_info[0] <= 2:
    py3 = False
    try:
        bytes
    except NameError:
        bytes = str
    base_string_type = basestring
elif sys.version_info[0] >= 3:
    py3 = True
    unicode = str
    base_string_type = str
    unichr = chr



#---- Test cases

class _SH2RTestCase(unittest.TestCase):
    """Helper class for Markdown tests."""

    maxDiff = None

    def _assertSimpleHtmlPath(self, html_path, encoding="utf-8", opts=None):
        html = codecs.open(html_path, 'r', encoding=encoding).read()
        rst_path = splitext(html_path)[0] + ".rst"
        rst = codecs.open(rst_path, 'r', encoding=encoding).read()
        self._assertSimpleHtml(html, rst, html_path, rst_path, opts=opts)

    def _assertSimpleHtml(self, html, rst, html_path=None, rst_path=None,
            opts=None):
        """Assert that markdown2.py produces the expected HTML."""
        if html_path is None: html_path = "<html content>"
        if rst_path is None: rst_path = "<rst content>"
        if opts is None:
            opts = {}

        actual_rst = simplehtml2rst.simplehtml2rst(html, **opts)

        diff = ''
        if actual_rst != rst:
            diff = difflib.unified_diff(
                    rst.splitlines(1),
                    actual_rst.splitlines(1),
                    rst_path,
                    "simplehtml2rst " + html_path)
            diff = ''.join(diff)
        errmsg = _dedent("""\
            simplehtml2rst.py didn't produce the expected RST:
              ---- html (escaping: .=space, \\n=newline) ----
            %s  ---- simplehtml2rst.py RST (escaping: .=space, \\n=newline) ----
            %s  ---- expected RST (escaping: .=space, \\n=newline) ----
            %s  ---- diff ----
            %s""") % (_display(html),
                      _display(actual_rst),
                      _display(rst),
                      _indent(diff))

        def charreprreplace(exc):
            if not isinstance(exc, UnicodeEncodeError):
                raise TypeError("don't know how to handle %r" % exc)
            if py3:
                obj_repr = repr(exc.object[exc.start:exc.end])[1:-1]
            else:
                # repr -> remote "u'" and "'"
                obj_repr = repr(exc.object[exc.start:exc.end])[2:-1]
            return (unicode(obj_repr), exc.end)
        codecs.register_error("charreprreplace", charreprreplace)

        self.assertEqual(actual_rst, rst, errmsg)

    def generate_tests(cls):
        """Add test methods to this class for each test file in
        `cls.cases_dir'.
        """
        cases_pat = join(dirname(__file__), cls.cases_dir, "*.html")
        for html_path in glob(cases_pat):
            # Load an options (`*.opts` file, if any).
            # It must be a Python dictionary. It will be passed as
            # kwargs to the markdown function.
            opts = {}
            opts_path = splitext(html_path)[0] + ".opts"
            if exists(opts_path):
                try:
                    opts = eval(open(opts_path, 'r').read())
                except Exception:
                    _, ex, _ = sys.exc_info()
                    print("WARNING: couldn't load `%s' opts file: %s" \
                          % (opts_path, ex))

            test_func = lambda self, t=html_path, o=opts: \
                self._assertSimpleHtmlPath(t, opts=o)

            tags_path = splitext(html_path)[0] + ".tags"
            if exists(tags_path):
                tags = []
                for line in open(tags_path):
                    if '#' in line: # allow comments in .tags files
                        line = line[:line.index('#')]
                    tags += line.split()
                test_func.tags = tags

            name = splitext(basename(html_path))[0]
            name = name.replace(' - ', '_')
            name = name.replace(' ', '_')
            name = re.sub("[(),]", "", name)
            test_name = "test_%s" % name
            setattr(cls, test_name, test_func)
    generate_tests = classmethod(generate_tests)

class CasesTestCase(_SH2RTestCase):
    cases_dir = "cases"

class DocTestsTestCase(unittest.TestCase):
    def test_api(self):
        test = doctest.DocFileTest("api.doctests")
        test.runTest()




#---- internal support stuff

_xml_escape_re = re.compile(r'&#(x[0-9A-Fa-f]{2,3}|[0-9]{2,3});')
def _xml_escape_sub(match):
    escape = match.group(1)
    if escape[0] == 'x':
        return unichr(int('0'+escape, base=16))
    else:
        return unichr(int(escape))

_markdown_email_link_re = re.compile(r'<a href="(.*?&#.*?)">(.*?)</a>', re.U)
def _markdown_email_link_sub(match):
    href, text = match.groups()
    href = _xml_escape_re.sub(_xml_escape_sub, href)
    text = _xml_escape_re.sub(_xml_escape_sub, text)
    return '<a href="%s">%s</a>' % (href, text)

def norm_html_from_html(html):
    """Normalize (somewhat) Markdown'd HTML.

    Part of Markdown'ing involves obfuscating email links with
    randomize encoding. Undo that obfuscation.

    Also normalize EOLs.
    """
    if not isinstance(html, unicode):
        html = html.decode('utf-8')
    html = _markdown_email_link_re.sub(
        _markdown_email_link_sub, html)
    if sys.platform == "win32":
        html = html.replace('\r\n', '\n')
    return html


def _display(s):
    """Markup the given string for useful display."""
    if not isinstance(s, unicode):
        s = s.decode("utf-8")
    s = _indent(_escaped_text_from_text(s, "whitespace"), 4)
    if not s.endswith('\n'):
        s += '\n'
    return s

def _markdown_with_perl(text):
    markdown_pl = join(dirname(__file__), "Markdown.pl")
    if not exists(markdown_pl):
        raise OSError("`%s' does not exist: get it from "
                      "http://daringfireball.net/projects/markdown/"
                      % markdown_pl)

    i, o = os.popen2("perl %s" % markdown_pl)
    i.write(text)
    i.close()
    html = o.read()
    o.close()
    return html


# Recipe: dedent (0.1.2)
def _dedentlines(lines, tabsize=8, skip_first_line=False):
    """_dedentlines(lines, tabsize=8, skip_first_line=False) -> dedented lines

        "lines" is a list of lines to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.

    Same as dedent() except operates on a sequence of lines. Note: the
    lines list is modified **in-place**.
    """
    DEBUG = False
    if DEBUG:
        print("dedent: dedent(..., tabsize=%d, skip_first_line=%r)"\
              % (tabsize, skip_first_line))
    indents = []
    margin = None
    for i, line in enumerate(lines):
        if i == 0 and skip_first_line: continue
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += tabsize - (indent % tabsize)
            elif ch in '\r\n':
                continue # skip all-whitespace lines
            else:
                break
        else:
            continue # skip all-whitespace lines
        if DEBUG: print("dedent: indent=%d: %r" % (indent, line))
        if margin is None:
            margin = indent
        else:
            margin = min(margin, indent)
    if DEBUG: print("dedent: margin=%r" % margin)

    if margin is not None and margin > 0:
        for i, line in enumerate(lines):
            if i == 0 and skip_first_line: continue
            removed = 0
            for j, ch in enumerate(line):
                if ch == ' ':
                    removed += 1
                elif ch == '\t':
                    removed += tabsize - (removed % tabsize)
                elif ch in '\r\n':
                    if DEBUG: print("dedent: %r: EOL -> strip up to EOL" % line)
                    lines[i] = lines[i][j:]
                    break
                else:
                    raise ValueError("unexpected non-whitespace char %r in "
                                     "line %r while removing %d-space margin"
                                     % (ch, line, margin))
                if DEBUG:
                    print("dedent: %r: %r -> removed %d/%d"\
                          % (line, ch, removed, margin))
                if removed == margin:
                    lines[i] = lines[i][j+1:]
                    break
                elif removed > margin:
                    lines[i] = ' '*(removed-margin) + lines[i][j+1:]
                    break
            else:
                if removed:
                    lines[i] = lines[i][removed:]
    return lines

def _dedent(text, tabsize=8, skip_first_line=False):
    """_dedent(text, tabsize=8, skip_first_line=False) -> dedented text

        "text" is the text to dedent.
        "tabsize" is the tab width to use for indent width calculations.
        "skip_first_line" is a boolean indicating if the first line should
            be skipped for calculating the indent width and for dedenting.
            This is sometimes useful for docstrings and similar.

    textwrap.dedent(s), but don't expand tabs to spaces
    """
    lines = text.splitlines(1)
    _dedentlines(lines, tabsize=tabsize, skip_first_line=skip_first_line)
    return ''.join(lines)

# Recipe: indent (0.2.1)
def _indent(s, width=4, skip_first_line=False):
    """_indent(s, [width=4]) -> 's' indented by 'width' spaces

    The optional "skip_first_line" argument is a boolean (default False)
    indicating if the first line should NOT be indented.
    """
    lines = s.splitlines(1)
    indentstr = ' '*width
    if skip_first_line:
        return indentstr.join(lines)
    else:
        return indentstr + indentstr.join(lines)


# Recipe: text_escape (0.1)
def _escaped_text_from_text(text, escapes="eol"):
    r"""Return escaped version of text.

        "escapes" is either a mapping of chars in the source text to
            replacement text for each such char or one of a set of
            strings identifying a particular escape style:
                eol
                    replace EOL chars with '\r' and '\n', maintain the actual
                    EOLs though too
                whitespace
                    replace EOL chars as above, tabs with '\t' and spaces
                    with periods ('.')
                eol-one-line
                    replace EOL chars with '\r' and '\n'
                whitespace-one-line
                    replace EOL chars as above, tabs with '\t' and spaces
                    with periods ('.')
    """
    #TODO:
    # - Add 'c-string' style.
    # - Add _escaped_html_from_text() with a similar call sig.
    import re

    if isinstance(escapes, base_string_type):
        if escapes == "eol":
            escapes = {'\r\n': "\\r\\n\r\n", '\n': "\\n\n", '\r': "\\r\r"}
        elif escapes == "whitespace":
            escapes = {'\r\n': "\\r\\n\r\n", '\n': "\\n\n", '\r': "\\r\r",
                       '\t': "\\t", ' ': "."}
        elif escapes == "eol-one-line":
            escapes = {'\n': "\\n", '\r': "\\r"}
        elif escapes == "whitespace-one-line":
            escapes = {'\n': "\\n", '\r': "\\r", '\t': "\\t", ' ': '.'}
        else:
            raise ValueError("unknown text escape style: %r" % escapes)

    # Sort longer replacements first to allow, e.g. '\r\n' to beat '\r' and
    # '\n'.
    escapes_keys = list(escapes.keys())
    try:
        escapes_keys.sort(key=lambda a: len(a), reverse=True)
    except TypeError:
        # Python 2.3 support: sort() takes no keyword arguments
        escapes_keys.sort(lambda a,b: cmp(len(a), len(b)))
        escapes_keys.reverse()
    def repl(match):
        val = escapes[match.group(0)]
        return val
    escaped = re.sub("(%s)" % '|'.join([re.escape(k) for k in escapes_keys]),
                     repl,
                     text)

    return escaped

def _one_line_summary_from_text(text, length=78,
        escapes={'\n':"\\n", '\r':"\\r", '\t':"\\t"}):
    r"""Summarize the given text with one line of the given length.

        "text" is the text to summarize
        "length" (default 78) is the max length for the summary
        "escapes" is a mapping of chars in the source text to
            replacement text for each such char. By default '\r', '\n'
            and '\t' are escaped with their '\'-escaped repr.
    """
    if len(text) > length:
        head = text[:length-3]
    else:
        head = text
    escaped = _escaped_text_from_text(head, escapes)
    if len(text) > length:
        summary = escaped[:length-3] + "..."
    else:
        summary = escaped
    return summary


#---- hook for testlib

def test_cases():
    """This is called by test.py to build up the test cases."""
    CasesTestCase.generate_tests()
    yield CasesTestCase
    yield DocTestsTestCase
