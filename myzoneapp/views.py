from distutils.dir_util import copy_tree
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
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
        if 'crawler' in request.COOKIES and request.COOKIES.get('crawler').startswith('myzonestatic'):
            return redirect(to='post_list')
        
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
    posts = [{
        'id': post.id,
        'title': post.title,
        'cover': post.cover,
        'date': post.date,
        'category': post.category.select_language(lang),
        'tags': [x.select_language(lang) for x in post.tags.all()],
        'draft': post.draft,
        'content': post.content
    } for post in posts_qs.filter(draft=False).order_by("-date").all()]
    ''' Pagination
    '''
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    current_str = request.GET.get("page", 1)
    try:
        current = int(current_str)
        if current < 1:
            return redirect(f'/post/?page=0')
        elif current > paginator.num_pages:
            return redirect(f'/post/?page={paginator.num_pages}')
        page = paginator.get_page(current)
        return render(request, 'post/list.html', {
            'posts': page.object_list,
            'pagination': None if paginator.num_pages <= 1 else {
                'page': page,
                'paginator': paginator.get_elided_page_range(current, on_each_side=2, on_ends=2),
                'tag_qs': f"&tag={tag_id}" if tag_id else "",
                'category_qs': f"&category={category_id}" if category_id else ""
            },
            **categories_tags,
            'show_not_categoried': Post.objects.filter(category__isnull=True).exists()
        })
    except ValueError:
        return redirect(r'/post/')


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
    if 'crawler' in request.COOKIES and request.COOKIES.get('crawler').startswith('myzonestatic'):
        return redirect(to='post_list')
    
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
    if 'crawler' in request.COOKIES and request.COOKIES.get('crawler').startswith('myzonestatic'):
        return redirect(to='post_list')
    
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
    if 'crawler' in request.COOKIES and request.COOKIES.get('crawler').startswith('myzonestatic'):
        return redirect(to='post_list')
    
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        post.delete()
        return redirect(to='post_list')


def user_login(request: HttpRequest):
    if 'crawler' in request.COOKIES and request.COOKIES.get('crawler').startswith('myzonestatic'):
        return redirect(to='home')
    
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
    if 'crawler' in request.COOKIES and request.COOKIES.get('crawler').startswith('myzonestatic'):
        return redirect(to='home')
    
    if get_user(request).is_authenticated:
        logout(request)
    
    redirect_to = request.GET.get('redirect') or 'home'
    return redirect(to=redirect_to)


def dist(request: HttpRequest):
    if not ((user := get_user(request)).is_authenticated and user.is_staff):
        return HttpResponseForbidden()
    
    dist_dir = settings.BASE_DIR / 'dist'
    if (not dist_dir.exists()):
        dist_dir.mkdir()
    request.COOKIES['django_language'] = 'zh-hans'
    request.COOKIES['crawler'] = 'myzonestatic'
    qd0 = request.GET
    ''' Home Page
    '''
    (dist_dir / 'index.html').write_bytes(home(request).content)
    ''' Posts
    '''
    post_dir = dist_dir / 'post'
    if (not post_dir.exists()):
        post_dir.mkdir()
    (post_dir / 'index.html').write_bytes(post_list(request).content)
    for post in Post.objects.all():
        post_page_dir = post_dir / f"{post.id}"
        if not post_page_dir.exists():
            post_page_dir.mkdir()
        (post_page_dir / 'index.html').write_bytes(post_page(request, post.id).content)
    ''' Categories
    '''
    if not (category_base := dist_dir / 'category').exists():
        category_base.mkdir()
    for category in Category.objects.all():
        category_dir = category_base / f"{category.id}"
        if not category_dir.exists():
            category_dir.mkdir()
        qd = QueryDict(f"category={category.id}")
        request.GET = qd
        (category_dir / 'index.html').write_bytes(post_list(request).content)
    ''' Tags
    '''
    if not (tag_base := dist_dir / 'tag').exists():
        tag_base.mkdir()
    for tag in Tag.objects.all():
        tag_dir = tag_base / f"{tag.id}"
        if not tag_dir.exists():
            tag_dir.mkdir()
        qd = QueryDict(f"tag={tag.id}")
        request.GET = qd
        (tag_dir / 'index.html').write_bytes(post_list(request).content)
    request.GET = qd0
    ''' static files
    '''
    copy_tree(settings.STATIC_ROOT.as_posix(), (dist_dir / 'static').as_posix())
    copy_tree(settings.MEDIA_ROOT.as_posix(), (dist_dir / 'media').as_posix())
    return HttpResponse(status=200)
