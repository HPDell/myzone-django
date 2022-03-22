import imp
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.core.files.storage import FileSystemStorage
from django.utils.translation import get_language_from_request
from pathlib import Path
from myzone import settings
from django.db.models import ImageField

from .models import Post, Category, Tag, Profile
from .forms import PostForm

# Create your views here.
def get_language_suffix_from_request(request: HttpRequest):
    return get_language_from_request(request).replace('-', '_')


def home(request: HttpRequest):
    """
    Home page. `/`
    """
    lang = get_language_suffix_from_request(request)
    posts = Post.objects.order_by("-date").all()[:5]
    adminUser = User.objects.get(pk=1)
    if (profile_qs := Profile.objects.filter(user=adminUser)).exists() and (profile := profile_qs.first()) is not None:
        return render(request, 'index.html', {
            'avatar': profile.avatar,
            'profile': profile.select_language(lang).content,
            'posts': posts
        })
    else:
        content = (settings.STATIC_ROOT / 'index.md').read_text()
        return render(request, 'index.html', {
            'profile': content,
            'posts': posts
        })


def get_categories_tags(request: HttpRequest):
    lang = get_language_suffix_from_request(request)
    categories = Category.objects.all()
    tags = Tag.objects.all()
    return {
        'categories': [{'id': x.id, 'name': x.select_language(lang).name} for x in categories],
        'tags': [{'id': x.id, 'name': x.select_language(lang).name} for x in tags]
    }


def post_list(request: HttpRequest):
    """
    Post list page. `/post/`
    """
    lang = get_language_suffix_from_request(request)
    ''' Get categories and tags
    '''
    categories_tags = get_categories_tags(request)
    ''' Drafts
    '''
    if request.GET.get('draft'):
        posts = Post.objects.filter(draft=True).order_by("-date").all()
        return render(request, 'post/list.html', {
            'posts': [{
                'id': post.id,
                'title': post.title,
                'cover': post.cover,
                'date': post.date,
                'category': post.category.select_language(lang),
                'tags': [x.select_language(lang) for x in post.tags.all()],
                'draft': post.draft,
                'content': post.content
            } for post in posts],
            **categories_tags,
            'show_not_categoried': Post.objects.filter(category__isnull=True).exists()
        })
    ''' Non-drafts
    '''
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
    posts = posts_qs.filter(draft=False).order_by("-date").all()
    return render(request, 'post/list.html', {
        'posts': [{
            'id': post.id,
            'title': post.title,
            'cover': post.cover,
            'date': post.date,
            'category': post.category.select_language(lang),
            'tags': [x.select_language(lang) for x in post.tags.all()],
            'draft': post.draft,
            'content': post.content
        } for post in posts],
        **categories_tags,
        'show_not_categoried': Post.objects.filter(category__isnull=True).exists()
    })


def post_page(request: HttpRequest, post_id: int):
    """
    Post detail page. `/post/id/`
    """
    lang = get_language_suffix_from_request(request)
    post: Post = get_object_or_404(Post, pk=post_id)
    return render(request, 'post/detail.html', {
        'post': {
            'id': post.id,
            'title': post.title,
            'cover': post.cover,
            'date': post.date,
            'category': post.category.select_language(lang),
            'tags': [x.select_language(lang) for x in post.tags.all()],
            'draft': post.draft,
            'content': post.content
        },
        # 'post_tags': post.tags.all(),
        **get_categories_tags(request),
        'show_not_categoried': Post.objects.filter(category__isnull=True).exists()
    })


@permission_required('myzoneapp.add_post')
def post_new(request: HttpRequest):
    """
    """
    if request.method == "GET":
        return render(request, 'post/edit.html', {
            **get_categories_tags(request)
        })
    
    elif request.method == "POST":
        lang = get_language_suffix_from_request(request)
        form = PostForm(request.POST)
        if form.is_valid():
            from_data = form.cleaned_data
            new_post = Post()
            new_post.title = from_data['title']
            if (new_cover := request.FILES.get('cover')) is not None:
                fss = FileSystemStorage()
                cover_file = request.FILES['cover']
                cover = fss.save(cover_file.name, cover_file)
                new_post.cover = cover
            new_post.date = from_data['date']
            category_name = from_data['category']
            if len(category_name) > 0:
                category_filter_options = { f"name_{lang}": category_name }
                if (category_query := Category.objects.filter(**category_filter_options)).exists():
                    category = category_query.first()
                else:
                    category = Category(**category_filter_options)
                    category.save()
                new_post.category = category
            else:
                new_post.category = None
            new_post.content = from_data['content']
            new_post.save()
            tag_name_list = request.POST.getlist('tags')
            for tag in tag_name_list:
                tags_filter_options = { f"name_{lang}": tag }
                if (tag_query := Tag.objects.filter(**tags_filter_options)).exists():
                    new_post.tags.add(tag_query.first())
                else:
                    tag_new = Tag(**tags_filter_options)
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
        lang = get_language_suffix_from_request(request)
        post = get_object_or_404(Post, pk=post_id)
        return render(request, 'post/edit.html', {
            **get_categories_tags(request),
            'post': {
                'id': post.id,
                'title': post.title,
                'cover': post.cover,
                'date': post.date,
                'category': post.category.select_language(lang).name,
                'tags': [x.select_language(lang).name for x in post.tags.all()],
                'draft': post.draft,
                'content': post.content
            }
        })
    
    elif request.method == "POST":
        lang = get_language_suffix_from_request(request)
        form = PostForm(request.POST)
        if form.is_valid():
            from_data = form.cleaned_data
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
            category_name = from_data['category']
            if len(category_name) > 0:
                category_filter_options = { f"name_{lang}": category_name }
                if (category_query := Category.objects.filter(**category_filter_options)).exists():
                    category = category_query.first()
                else:
                    category = Category(**category_filter_options)
                    category.save()
                new_post.category = category
            else:
                new_post.category = None
            new_post.draft = True if 'draft' in request.POST else False
            new_post.content = from_data['content']
            new_post.save()
            tag_name_list = request.POST.getlist('tags')
            for tag in tag_name_list:
                tags_filter_options = { f"name_{lang}": tag }
                if (tag_query := Tag.objects.filter(**tags_filter_options)).exists():
                    new_post.tags.add(tag_query.first())
                else:
                    tag_new = Tag(**tags_filter_options)
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
        if get_user(request).is_authenticated:
            return redirect(to=redirect_to)
        else:
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
    if get_user(request).is_authenticated:
        logout(request)
    redirect_to = request.GET.get('redirect') or 'home'
    return redirect(to=redirect_to)