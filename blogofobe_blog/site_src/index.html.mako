<%inherit file="_templates/site.mako" />
<article class="page_box">
<%self:filter chain="markdown">

Welcome to blogofobe
====================

This is an example [blogofobe](http://github.com/wxl/blogofobe) site that is
optimized for HTML5 browsers.

Please see the [Documentation](http://www.blogofobe.com/documentation)
for getting started and for customizing your site.

Specific customization points for this example:

 * ``_templates/theme.mako`` imports the stylesheet and a few custom web fonts from [Google's CDN](http://www.google.com/webfonts).
 * To change the twitter search for the widget on the right, see ``js/site.js`` and ``_templates/sidebar.mako``.
</%self:filter>
</article>
