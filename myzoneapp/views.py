import imp
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from myzone import settings
from django.db.models import ImageField

from .models import Post, Category, Tag, Profile
from .forms import PostForm

# Create your views here.
def home(request: HttpRequest):
    """
    Home page. `/`
    """
    posts = Post.objects.order_by("-date").all()[:5]
    adminUser = User.objects.get(pk=1)
    if (profile_qs := Profile.objects.filter(user=adminUser)).exists():
        profile = profile_qs.first()
        return render(request, 'index.html', {
            'avatar': profile.avatar,
            'profile': profile.content,
            'posts': posts
        })
    else:
        content = (settings.STATICFILES_DIRS[0] / 'index.md').read_text()
        return render(request, 'index.html', {
            'profile': content,
            'posts': posts
        })


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


@permission_required('myzoneapp.add_post')
def post_new(request: HttpRequest):
    """
    """
    if request.method == "GET":
        categories = Category.objects.all()
        tags = Tag.objects.all()
        return render(request, 'post/edit.html', {
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
            if (new_cover := request.FILES.get('cover')) is not None:
                fss = FileSystemStorage()
                cover_file = request.FILES['cover']
                cover = fss.save(cover_file.name, cover_file)
                new_post.cover = cover
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


@permission_required('myzoneapp.change_post')
def post_edit(request: HttpRequest, post_id: int):
    """
    """
    if request.method == "GET":
        post = get_object_or_404(Post, pk=post_id)
        categories = Category.objects.all()
        tags = Tag.objects.all()
        return render(request, 'post/edit.html', {
            'categories': categories,
            'tags': tags,
            'post': post,
            'post_tags': [x.name for x in post.tags.all()]
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
            new_post: Post = get_object_or_404(Post, pk=post_id)
            new_post.title = from_data['title']
            old_cover: ImageField = new_post.cover
            if (new_cover := request.FILES.get('cover')) is not None:
                fss = FileSystemStorage()
                if old_cover:
                    fss.delete(old_cover.name)
                cover = fss.save(new_cover.name, new_cover)
                new_post.cover = cover
            elif request.POST.get('cover_delete'):
                if old_cover:
                    old_cover.storage.delete(old_cover.name)
                    new_post.cover = None
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


@permission_required('myzoneapp.delete_post')
def post_delete(request: HttpRequest, post_id: int):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        post.delete()
        return redirect(to='post_list')


def user_login(request: HttpRequest):
    if request.method == 'GET':
        redirect_to = request.GET.get('redirect') or 'home'
        return render(request, 'login.html', {
            'redirect': redirect_to
        })
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect_to = request.POST.get('redirect') or 'home'
            return redirect(to=redirect_to)
        else:
            return HttpResponseForbidden()


def user_logout(request: HttpRequest):
    logout(request)
    redirect_to = request.GET.get('redirect') or 'home'
    return redirect(to=redirect_to)