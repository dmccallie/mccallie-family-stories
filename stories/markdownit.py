from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin

md = MarkdownIt("gfm-like", {
    "typographer": True,
    "breaks": True,
}).use(footnote_plugin)
md.enable(["replacements", "smartquotes"])
md.disable(["linkify"])

print("initialized markdownit instance.")

