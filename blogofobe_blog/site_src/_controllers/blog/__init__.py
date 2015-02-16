# -*- coding: utf-8 -*-
import os
import logging
try:
    from urllib.parse import urlparse   # For Python 2
except ImportError:
    from urlparse import urlparse       # For Python 3; flake8 ignore # NOQA
import six
from blogofobe.cache import bf
from blogofobe.cache import HierarchicalCache as HC
import blogofobe_blog


meta = {
    "name": "Blog",
    "author": "Ryan McGuire",
    "description": "Creates a Blog",
    "version": "0.8",
}
blog = config = bf.config.plugins.blog
tools = blogofobe_blog.tools


def iter_posts(conditional, limit=None):
    """Iterate over all the posts for which conditional(post) == True.
    """
    num_yielded = 0
    for post in blog.posts:
        if conditional(post):
            num_yielded += 1
            yield post
        if limit and num_yielded >= limit:
            break


def iter_posts_published(limit=None):
    """Iterate over all the posts to be published"""
    def is_publishable(post):
        if post.draft is False and post.permalink is not None:
            return True
    return iter_posts(is_publishable, limit)


def init():
    config["url"] = bf.config.site.url + config["path"]
    if config.template_path:
        #Add the user's custom template paths first
        if isinstance(config.template_path, six.string_types):
            template_paths = [config.template_path]
        else:
            template_paths = config.template_path
        for tp in template_paths:
            tools.add_template_dir(tp, append=False)
    tools.add_template_dir(
        os.path.join(tools.get_src_dir(), "_templates/blog"))


def run():
    # TODO: Move imports to top of file, if possible.
    from . import post
    from . import archives
    from . import categories
    from . import tags
    from . import chronological
    from . import feed
    from . import permapage
    blog.logger = logging.getLogger(config['name'])
    #Parse the posts
    blog.posts = post.parse_posts(blog.post.source_dir)
    if blog.post.post_process:
        #The user may define their own callback to process posts after
        #they have been parsed but before we've done any actual work.
        blog.post.post_process()
    blog.iter_posts = iter_posts
    blog.iter_posts_published = iter_posts_published
    blog.dir = bf.util.fs_site_path_helper(bf.writer.output_dir, blog.path)
    # Find all the categories and archives before we write any pages
    blog.archived_posts = {}    # "/archive/Year/Month" -> [post, post, ... ]
    blog.archive_links = []     # [("/archive/2009/12", name,
                                #   num_in_archive1), ...]
                                # (sorted in reverse by date)
    blog.categorized_posts = {} # "Category Name" -> [post, post, ... ]
    blog.tagged_posts = {}      # "Tag Name" -> [post, post, ... ]
    blog.all_categories = []    # [("Category 1",num_in_category_1), ...]
                                # (sorted alphabetically)
    blog.all_tags = []          # [("Tag 1",num_in_tag_1), ...]
                                # (sorted alphabetically)
    archives.sort_into_archives()
    categories.sort_into_categories()
    tags.sort_into_tags()
    permapage.run()
    chronological.run()
    archives.run()
    categories.run()
    tags.run()
    feed.run()
