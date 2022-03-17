from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.http.request import HttpRequest

from .models import Post, Category, Tag
from .forms import PostForm

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
    posts_qs = None
    ''' Filter by categories
    '''
    if (category_id := request.GET.get('category')) is not None:
        if category_id == 'null':
            posts_qs = Post.objects.filter(category__isnull=True)
        elif (category := Category.objects.filter(pk=category_id).first()) is not None:
            posts_qs = Post.objects.filter(category=category)
        else:
            posts_qs = Post.objects
    ''' Filter by tags
    '''
    if (tag_id := request.GET.get('tag')) is not None:
        if (tag := Tag.objects.filter(pk=tag_id).first()) is not None:
            posts_qs = Post.objects.filter(tags=tag)
        else:
            posts_qs = Post.objects
    ''' If not filtered, return all data.
    '''
    posts_qs = Post.objects if posts_qs is None else posts_qs
    posts = posts_qs.order_by("-date").all()
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
        'post_tags': post.tags.all(),
        'category': categories,
        'tags': tags
    })

def post_new(request: HttpRequest):
    """
    """
    if request.method == "GET":
        categories = Category.objects.all()
        tags = Tag.objects.all()
        return render(request, 'post/new.html', {
            'categories': categories,
            'tags': tags
        })
    
    elif request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            from_data = form.cleaned_data
            category_name = from_data['category']
            if (category_query := Category.objects.filter(name=category_name)).exists():
                category = category_query.first()
            else:
                category = Category(name=category_name)
                category.save()
            new_post = Post()
            new_post.title = from_data['title']
            new_post.cover = from_data['cover']
            new_post.date = from_data['date']
            new_post.category = category
            new_post.content = from_data['content']
            new_post.save()
            tag_name_list = request.POST.getlist('tags')
            for tag in tag_name_list:
                if (tag_query := Tag.objects.filter(name=tag)).exists():
                    new_post.tags.add(tag_query.first())
                else:
                    tag_new = Tag(name=tag)
                    tag_new.save()
                    new_post.tags.add(tag_new)
            return redirect(to='post_page', post_id=new_post.id)
        else:
            return HttpResponseBadRequest()