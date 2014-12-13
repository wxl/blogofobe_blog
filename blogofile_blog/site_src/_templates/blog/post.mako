<%page args="post"/>

<% 
   category_links = []
   for category in post.categories:
       if post.draft:
           #for drafts, we don't write to the category dirs, so just write the categories as text
           category_links.append(category.name)
       else:
           category_links.append("<a href='%s'>%s</a>" % (category.path, category.name))
%>

<% 
   tag_links = []
   for tag in post.tags:
       if post.draft:
           #for drafts, we don't write to the tag dirs, so just write the tags as text
           tag_links.append(tag.name)
       else:
           tag_links.append("<a href='%s'>%s</a>" % (tag.path, tag.name))
%>

<article>
  <div class="blog_post">
    <header>
      <div id="${post.slug}"></div>
      <h2 class="blog_post_title"><a href="${post.permapath()}" rel="bookmark" title="Permanent Link to ${post.title}">${post.title}</a></h2>
      <p><small><span class="blog_post_date">${post.date.strftime("%B %d, %Y at %I:%M %p")}</span> | categories: 
        <span class="blog_post_categories">${", ".join(category_links)}</span> | tags:
        <span class="blog_post_tags">${", ".join(tag_links)}</span> 
        % if bf.config.blog.disqus.enabled:
        | <a href="${post.permalink}#disqus_thread">View Comments</a>
        % endif
      </small></p>
    </header>
    <div class="post_prose">
      ${self.post_prose(post)}
    </div>
  </div>
</article>

<%def name="post_prose(post)">
${post.content}
</%def>
