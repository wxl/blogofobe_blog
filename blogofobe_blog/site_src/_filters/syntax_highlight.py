# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import os

import pygments
from pygments import formatters, util, lexers
import six
from blogofobe.cache import HierarchicalCache as HC
import blogofobe_bf as bf

#Example usage:
"""

This is normal text.

The following is a python code block:

$$code(lang=python)
import this

prices = {'apple' : 0.50,    #Prices of fruit
          'orange' : 0.65,
          'pear' : 0.90}

def print_prices():
    for fruit, price in prices.items():
        print "An %s costs %s" % (fruit, price)
$$/code

This is a ruby code block:

$$code(lang=ruby)
class Person
  attr_reader :name, :age
  def initialize(name, age)
    @name, @age = name, age
  end
  def <=>(person) # Comparison operator for sorting
    @age <=> person.age
  end
  def to_s
    "#@name (#@age)"
  end
end

group = [
  Person.new("Bob", 33),
  Person.new("Chris", 16),
  Person.new("Ash", 23)
]

puts group.sort.reverse
$$/code

This is normal text
"""

meta = {"name": "Syntax Highlighter",
        "description": "Highlights blocks of code based on syntax",
        "author": "Ryan McGuire"}

config = HC(
        css_dir = "/css",
        preload_styles = [],
        style = "murphy")

def init():
    #This filter normally only loads pygments styles when needed.
    #This will force a particular style to get loaded at startup.
    for style in config.preload_styles:
        css_class = "pygments_{0}".format(style)
        formatter = pygments.formatters.HtmlFormatter(
            linenos=False, cssclass=css_class, style=style)
        write_pygments_css(style, formatter)


css_files_written = set()

code_block_re = re.compile(
    r"(?:^|\s)"                 # $$code Must start as a new word
    r"\$\$code"                 # $$code is the start of the block
    r"(?P<args>\([^\r\n]*\))?"  # optional arguments are passed in brackets
    r"[^\r\n]*\r?\n"            # ignore everything else on the 1st line
    r"(?P<code>.*?)\s\$\$/code" # code block continues until $$/code
    , re.DOTALL)

argument_re = re.compile(
    r"[ ]*" # eat spaces at the beginning
    "(?P<arg>" # start of argument
    ".*?" # the name of the argument
    "=" # the assignment
    r"""(?:(?:[^"']*?)""" # a non-quoted value
    r"""|(?:"[^"]*")""" # or, a double-quoted value
    r"""|(?:'[^']*')))""" # or, a single-quoted value
    "[ ]*" # eat spaces at the end
    "[,\r\n]" # ends in a comma or newline
    )

def highlight_code(code, language, formatter):
    try:
        lexer = pygments.lexers.get_lexer_by_name(language)
    except pygments.util.ClassNotFound:
        lexer = pygments.lexers.get_lexer_by_name("text")
    #Highlight with pygments
    highlighted = pygments.highlight(code, lexer, formatter)
    #Convert line endings to <br> tags:
    highlighted = highlighted.replace("\n","<br/>")
    #But get rid of the last <br> which throws off line numbers:
    highlighted = "</pre></div>".join(highlighted.rsplit("</pre></div><br/>"))
    #Surround the text with newlines so markdown etc parse properly:
    highlighted = six.u("\n\n{0}\n\n").format(highlighted)
    return highlighted

def parse_args(args):
    #Make sure the args are newline terminated (req'd by regex)
    opts = {}
    if args is None:
        return opts
    args = args.lstrip("(").rstrip(")")
    if args[-1] != "\n":
        args = args+"\n"
    for m in argument_re.finditer(args):
        arg = m.group('arg').split('=')
        opts[arg[0]] = arg[1]
    return opts


def write_pygments_css(style, formatter,
        location=config.css_dir):
    path = bf.util.path_join("_site", bf.util.fs_site_path_helper(location))
    bf.util.mkdir(path)
    css_file = "pygments_{0}.css".format(style)
    css_path = os.path.join(path, css_file)
    css_site_path = css_path.replace("_site", "")
    if css_site_path in css_files_written:
        return #already written, no need to overwrite it.
    f = open(css_path, "w")
    css_class = ".pygments_{0}".format(style)
    f.write(formatter.get_style_defs(css_class))
    f.close()
    css_files_written.add(css_site_path)


def run(src):
    substitutions = {}
    for m in code_block_re.finditer(src):
        args = parse_args(m.group('args'))
        #Make default args
        if 'lang' in args:
            lang = args['lang']
        elif 'language' in args:
            lang = args['language']
        else:
            lang = 'text'
        try:
            if 'linenums' in args:
                linenums = args['linenums']
            elif "linenos" in args:
                linenums = args['linenos']
            if linenums.lower().strip() == "true":
                linenums = True
            else:
                linenums = False
        except:
            linenums = False
        try:
            style = args['style']
        except KeyError:
            style = config.style
        try:
            css_class = args['cssclass']
        except KeyError:
            css_class = "pygments_{0}".format(style)
        css_class += " syntax_highlight"
        formatter = pygments.formatters.HtmlFormatter(
            linenos=linenums, cssclass=css_class, style=style)
        write_pygments_css(style, formatter)
        substitutions[m.group()] = highlight_code(
                m.group('code'), lang, formatter)
    if len(substitutions) > 0:
        p = re.compile('|'.join(map(re.escape, substitutions)))
        src = p.sub(lambda x: substitutions[x.group(0)], src)
        return src
    else:
        return src
