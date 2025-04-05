from typing import Optional
from datetime import datetime
from xml.sax.saxutils import XMLGenerator
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import get_language, get_language_info
from dataclasses import dataclass
from markdown2 import Markdown
from .models import Post, PostTranslate
from myzone import settings
from bs4 import BeautifulSoup


@dataclass
class PostItem:
    title: str
    description: str
    link: Optional[str]
    pubdate: datetime


class FollowFeed(Rss201rev2Feed):
    follow_feed_id = settings.FOLLOW_FEED_ID["zh-hans"]
    follow_user_id = settings.FOLLOW_USER_ID

    def __init__(self, title, link, description, language = ..., author_email = ..., author_name = ..., author_link = ..., subtitle = ..., categories = ..., feed_url = ..., feed_copyright = ..., feed_guid = ..., ttl = ..., **kwargs):
        super().__init__(title, link, description, language, author_email, author_name, author_link, subtitle, categories, feed_url, feed_copyright, feed_guid, ttl, **kwargs)
        self.follow_feed_id = settings.FOLLOW_FEED_ID[language]
    
    def add_root_elements(self, handler: XMLGenerator):
        super().add_root_elements(handler)
        handler.startElement("follow_challenge", {})
        handler.startElement("feedId", {})
        handler.characters(self.follow_feed_id)
        handler.endElement("feedId")
        handler.startElement("userId", {})
        handler.characters(self.follow_user_id)
        handler.endElement("userId")
        handler.endElement("follow_challenge")


class LatestPostFeed(Feed):
    feed_type = FollowFeed

    def __call__(self, request, *args, **kwargs):
        self.request = request
        return super().__call__(request, *args, **kwargs)

    def title(self):
        lang = get_language()
        lang_name = get_language_info(lang)["name_local"]
        return settings.FEED_TITLE_BASE + " " + (f"({lang_name})" if lang != "zh-hans" else "")
    
    def description(self):
        return settings.FEED_DESCRIPTION[get_language()]

    def link(self):
        return f"{self.request.scheme}://{self.request.get_host()}{reverse('post_list')}"

    def fix_html_img_src(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and not src.startswith(("http://", "https://")):
                img["src"] = f"{self.request.scheme}://{self.request.get_host()}{src}"
        return str(soup)

    def items(self):
        post_trans = PostTranslate.objects.filter(language=get_language())
        posts_qs = Post.objects.filter(pk__in=[x.post.id for x in post_trans])
        posts: list[Post] = posts_qs.filter(draft=False).order_by("-date")[:10]
        renderer = Markdown(extras=[
            'latex', 'footnotes', 'tables', 'strike', 'mermaid', 'task_list',
            'code-friendly', 'fenced-code-blocks'
        ])
        post_items = [PostItem(
            title=post.title,
            description=self.fix_html_img_src(renderer.convert(post.content)),
            link=reverse('post_page', args=[post.permanent]),
            pubdate=datetime(post.date.year, post.date.month, post.date.day)
        ) for post in posts]
        return post_items
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return f"{self.request.scheme}://{self.request.get_host()}{item.link}"

    def item_pubdate(self, item):
        return item.pubdate
