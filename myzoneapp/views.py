from django.shortcuts import get_object_or_404, render

from myzoneapp.models import Post, Category, Tag

# Create your views here.
def post_list(request):
    posts = Post.objects.all()
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'posts/list.html', {
        'posts': posts,
        'category': categories,
        'tags': tags
    })


def post_page(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, 'posts/detail.html', {
        'post': post,
        'category': categories,
        'tags': tags
    })
