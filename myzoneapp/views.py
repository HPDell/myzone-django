from django.shortcuts import get_object_or_404, render
from django.http.request import HttpRequest

from myzoneapp.models import Post, Category, Tag

# Create your views here.
def home(request: HttpRequest):
    """
    Home page. `/`
    """
    return render(request, 'index.html')


def post_list(request: HttpRequest):
    """
    Post list page. `/post/`
    """
    posts = None
    ''' Filter by categories
    '''
    if (category_id := request.GET.get('category')) is not None:
        if category_id == 'null':
            posts = Post.objects.filter(category__isnull=True).all()
        elif (category := Category.objects.filter(pk=category_id).first()) is not None:
            posts = Post.objects.filter(category=category).all()
        else:
            posts = Post.objects.all()
    ''' Filter by tags
    '''
    if (tag_id := request.GET.get('tag')) is not None:
        if (tag := Tag.objects.filter(pk=tag_id).first()) is not None:
            posts = Post.objects.filter(tags=tag).all()
        else:
            posts = Post.objects.all()
    ''' If not filtered, return all data.
    '''
    posts = Post.objects.all() if posts is None else posts
    ''' Get other data
    '''
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'post/list.html', {
        'posts': posts,
        'category': categories,
        'tags': tags
    })


def post_page(request: HttpRequest, post_id: int):
    """
    Post detail page. `/post/id/`
    """
    post = get_object_or_404(Post, pk=post_id)
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'post/detail.html', {
        'post': post,
        'category': categories,
        'tags': tags
    })
