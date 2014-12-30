# -*- coding: utf-8 -*-
import shutil
import operator
from blogofobe.cache import bf

from . import blog, tools
from . import feed


def run():
    write_tags()


def sort_into_tags():
    tags = set()
    for post in blog.iter_posts_published():
        tags.update(post.tags)
    for tag in tags:
        tag_posts = [post for post in blog.iter_posts_published()
                            if tag in post.tags]
        blog.tagged_posts[tag] = tag_posts
    for tag, posts in sorted(
        list(blog.tagged_posts.items()), key=operator.itemgetter(0)):
        blog.all_tags.append((tag, len(posts)))


def write_tags():
    """Write all the blog posts in tags.
    """
    root = bf.util.path_join(blog.path, blog.tag_dir)
    #Find all the tags:
    tags = set()
    for post in blog.iter_posts_published():
        tags.update(post.tags)
    for tag, tag_posts in list(blog.tagged_posts.items()):
        page_num = 1
        while True:
            path = bf.util.path_join(root, tag.url_name,
                                str(page_num), "index.html")
            page_posts = tag_posts[:blog.posts_per_page]
            tag_posts = tag_posts[blog.posts_per_page:]
            #Forward and back links
            if page_num > 1:
                prev_link = bf.util.site_path_helper(
                    blog.path, blog.tag_dir, tag.url_name,
                                           str(page_num - 1))
            else:
                prev_link = None
            if len(tag_posts) > 0:
                next_link = bf.util.site_path_helper(
                    blog.path, blog.tag_dir, tag.url_name,
                                           str(page_num + 1))
            else:
                next_link = None
            env = {
                "tag": tag,
                "posts": page_posts,
                "prev_link": prev_link,
                "next_link": next_link,
                "page_num": page_num
            }
            tools.materialize_template("chronological.mako", path, env)
            #Copy tag/1 to tag/index.html
            if page_num == 1:
                shutil.copyfile(
                        bf.util.path_join(bf.writer.output_dir, path),
                        bf.util.path_join(
                                bf.writer.output_dir, root, tag.url_name,
                                "index.html"))
            #Prepare next iteration
            page_num += 1
            if len(tag_posts) == 0:
                break
