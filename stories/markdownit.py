from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin

# from mdit_plain.renderer import RendererPlain

md = MarkdownIt("gfm-like", {
    "typographer": True,
    "breaks": True,
}).use(footnote_plugin)
md.enable(["replacements", "smartquotes"])
md.disable(["linkify"])

print("initialized markdownit instance.")

# plain_renderer = MarkdownIt(renderer_cls=RendererPlain)
# print("initialized plain_render instance. Test = ", plain_render.render("# Hello **World**!"))

