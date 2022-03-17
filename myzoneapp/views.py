from django.shortcuts import get_object_or_404, render

from myzoneapp.models import Post, Category, Tag

# Create your views here.
def home(request):
    """
    Home page. `/`
    """
    return render(request, 'index.html')


def post_list(request):
    """
    Post list page. `/post/`
    """
    posts = Post.objects.all()
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'post/list.html', {
        'posts': posts,
        'category': categories,
        'tags': tags
    })


def post_page(request, post_id):
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
