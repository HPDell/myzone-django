from typing import Optional
from datetime import datetime
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.translation import get_language
from dataclasses import dataclass
from .models import Post, PostTranslate
from markdown2 import Markdown

FEED_DESCRIPTION = {
    "zh-hans": "HPDell的个人博客",
    "en": "HPDell's Blog",
}

CLAIM_DESCRIPTION = {
    "zh-hans": "feedId:106084893890443264+userId:46662346918514688",
    "en": "feedId:106090697091066880+userId:46662346918514688",
}

@dataclass
class PostItem:
    title: str
    description: str
    link: Optional[str]
    pubdate: datetime

class LatestPostFeed(Feed):
    title = "HPDell's Zone"
    
    def description(self):
        return " ".join([FEED_DESCRIPTION[get_language()], CLAIM_DESCRIPTION[get_language()]])

    def link(self):
        return reverse('post_list')

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
            description=renderer.convert(post.content),
            link=reverse('post_page', args=[post.permanent]),
            pubdate=datetime(post.date.year, post.date.month, post.date.day)
        ) for post in posts]
        return post_items
    
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.link

    def item_pubdate(self, item):
        return item.pubdate
