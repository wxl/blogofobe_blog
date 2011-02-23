import os
import logging
import urlparse
from mako.lookup import TemplateLookup

from blogofile.cache import bf
from blogofile.cache import HierarchicalCache as HC

import blogofile_blog

meta = {
    "name": "Blog",
    "author": "Ryan McGuire",
    "description": "Creates a Blog",
    "version": "0.8",
    }

config = HC(
        # name -- Your Blog's name.
        # This is used repeatedly in default blog templates
        name = "Your Blog's name",
        ## blog_description -- A short one line description of the blog
        # used in the RSS/Atom feeds.
        description = "Your Blog's short description",
        ## blog_path -- Blog path.
        #  This is the path of the blog relative to the site_url.
        #  If your site_url is "http://www.yoursite.com/~ryan"
        #  and you set blog_path to "/blog" your full blog URL would be
        #  "http://www.yoursite.com/~ryan/blog"
        #  Leave blank "" to set to the root of site_url
        path = "/blog",
        ## blog_timezone -- the timezone that you normally write your blog posts from
        timezone = "US/Eastern",
        ## blog_posts_per_page -- Blog posts per page
        posts_per_page = 5,
        # Automatic Permalink
        # (If permalink is not defined in post article, it's generated
        #  automatically based on the following format:)
        # Available string replacements:
        # :year, :month, :day -> post's date
        # :title              -> post's title
        # :uuid               -> sha hash based on title
        # :filename           -> article's filename without suffix
        # path is relative to site_url
        auto_permalink = HC(enabled=True,
                             path=":blog_path/:year/:month/:day/:title"),
        #### Disqus.com comment integration ####
        disqus = HC(enabled=False,
                     name="your_disqus_name"),
        #### Custom blog index ####
        # If you want to create your own index page at your blog root
        # turn this on. Otherwise blogofile assumes you want the
        # first X posts displayed instead
        custom_index = False,
        #### Post excerpts ####
        # If you want to generate excerpts of your posts in addition to the
        # full post content turn this feature on
        #Also, if you don't like the way the post excerpt is generated
        #You can define assign a new function to blog.post_excerpts.method
        #This method must accept the following arguments: (content, num_words)
        post_excerpts = HC(enabled=True,
                            word_length=25),
        #### Blog pagination directory ####
        # blogofile places extra pages of your blog in
        # a secondary directory like the following:
            # http://www.yourblog.com/blog_root/page/4
        # You can rename the "page" part here:
        pagination_dir = "page",
        #### Blog category directory ####
        # blogofile places extra pages of your or categories in
        # a secondary directory like the following:
        # http://www.yourblog.com/blog_root/category/your-topic/4
        # You can rename the "category" part here:
        category_dir = "category",
        priority = 90.0,
        base_template = "site.mako",
        template_path = "_templates/blog",
        #Posts
        post = HC(
            date_format = "%Y/%m/%d %H:%M:%S",
            encoding = "utf-8",
            #### Default post filters ####
            # If a post does not specify a filter chain, use the
            # following defaults based on the post file extension:
            default_filters = {
               "markdown": "syntax_highlight, markdown",
               "textile": "syntax_highlight, textile",
               "org": "syntax_highlight, org",
               "rst": "syntax_highlight, rst",
               "html": "syntax_highlight"
               }
            )
        )

tools = blogofile_blog.tools

def init():
    config["url"] = urlparse.urljoin(bf.config.site.url, config["path"])
    #The base template is a configurable option, injected here at runtime:
    tools.template_lookup.put_template(
        "blog_base_template",tools.template_lookup.get_template(
            config["base_template"]))
    tools.add_template_dir(os.path.join(tools.get_src_dir(),config.template_path))

def run():
    blog = config

    #Parse the posts
    import post
    import archives
    import categories
    import chronological
    import feed
    import permapage
    blog.posts = post.parse_posts("_posts")
    blog.dir = bf.util.path_join(bf.writer.output_dir, blog.path)

    # Find all the categories and archives before we write any pages
    blog.archived_posts = {} ## "/archive/Year/Month" -> [post, post, ... ]
    blog.archive_links = []  ## [("/archive/2009/12", name, num_in_archive1), ...] (sorted in reverse by date)
    blog.categorized_posts = {} ## "Category Name" -> [post, post, ... ]
    blog.all_categories = [] ## [("Category 1",num_in_category_1), ...] (sorted alphabetically)
    archives.sort_into_archives()
    categories.sort_into_categories()

    blog.logger = logging.getLogger(config['name'])

    permapage.run()
    chronological.run()
    archives.run()
    categories.run()
    feed.run()
