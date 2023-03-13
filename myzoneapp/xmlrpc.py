from django.contrib.auth import authenticate
from modernrpc.core import rpc_method, RPCInvalidParams
from .models import Post

@rpc_method(name="blogger.getUsersBlogs")
def get_users_blogs(key, username, password):
    user = authenticate(username=username, password=password)
    if user is not None:
        return [{
            "blogId": "myzone",
            "blogName": "myzone"
        }]
    else:
        raise RPCInvalidParams

@rpc_method(name="metaWeblog.getRecentPosts")
def get_recent_posts(blogid, username, password, numberOfPosts):
    user = authenticate(username=username, password=password)
    if user is not None:
        posts = Post.objects.order_by("-date").all()
        return [{
            "postid": post.permanent.title,
            "title": post.title,
            "description": post.content,
            "dateCreated": post.date,
            "categories": post.category
        } for post in posts]
    else:
        raise RPCInvalidParams