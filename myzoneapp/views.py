from django.shortcuts import get_object_or_404, redirect, render
from django.http.request import HttpRequest
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied, BadRequest
from django.utils.translation import get_language_from_request
from pathlib import Path
from myzone import settings
from django.db.models import ImageField, Count

from .models import Post, Category, Tag, Profile, Publication, PostTranslate, PostPermanent
from .forms import PostForm

# Create your views here.
def get_language_suffix_from_request(request: HttpRequest):
    return get_language_from_request(request).replace('-', '_')


def home(request: HttpRequest):
    """
    Home page. `/`
    """
    lang = get_language_suffix_from_request(request)
    posts = Post.objects.filter(draft=False).order_by("-date").all()[:5]
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
    post_trans = PostTranslate.objects.filter(language=get_language_from_request(request))
    post_permanent = PostPermanent.objects.filter(pk__in=[x.permanent.id for x in post_trans])
    posts_qs = Post.objects.filter(permanent__in=post_permanent)
    ''' Get categories and tags
    '''
    categories_tags = get_categories_tags(request)
    ''' Drafts
    '''
    if request.GET.get('draft'):
        if not request.user.is_authenticated:
            raise PermissionDenied

        posts = posts_qs.filter(draft=True).order_by("-date").all()
        return render(request, 'post/list.html', {
            'posts': [{
                'id': post.id,
                'title': post.title,
                'cover': post.cover,
                'date': post.date,
                'category': post.category.select_language(lang) if post.category else None,
                'tags': [x.select_language(lang) for x in post.tags.all()],
                'draft': post.draft,
                'content': post.content,
                'permanent': post.permanent.title
            } for post in posts],
            **categories_tags,
            'show_not_categoried': Post.objects.filter(category__isnull=True).exists()
        })
    ''' Non-drafts
    '''
    if (category_id := request.GET.get('category')) is not None:
        ''' Filter by categories
        '''
        if category_id == 'null':
            posts_qs = posts_qs.filter(category__isnull=True)
        elif (category := Category.objects.filter(pk=category_id).first()) is not None:
            posts_qs = posts_qs.filter(category=category)
        else:
            posts_qs = posts_qs
    if (tag_id := request.GET.get('tag')) is not None:
        ''' Filter by tags
        '''
        if (tag := Tag.objects.filter(pk=tag_id).first()) is not None:
            posts_qs = posts_qs.filter(tags=tag)
        else:
            posts_qs = posts_qs
    ''' If not filtered, return all data.
    '''
    posts = [{
        'id': post.id,
        'title': post.title,
        'cover': post.cover,
        'date': post.date,
        'category': post.category.select_language(lang) if post.category else None,
        'tags': [x.select_language(lang) for x in post.tags.all()],
        'draft': post.draft,
        'content': post.content,
        'permanent': post.permanent.title
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


def post_page(request: HttpRequest, permanent_title: str):
    """
    Post detail page. `/post/id/`
    """
    lang = get_language_suffix_from_request(request)
    permanent = get_object_or_404(PostPermanent, title=permanent_title)
    post_trans = get_object_or_404(PostTranslate, permanent=permanent, language=get_language_from_request(request))
    post: Post = get_object_or_404(Post, pk=post_trans.post.id)
    
    if post.draft:
        if not request.user.is_authenticated:
            raise PermissionDenied

    return render(request, 'post/detail.html', {
        'post': {
            'id': post.id,
            'title': post.title,
            'cover': post.cover,
            'date': post.date,
            'category': post.category.select_language(lang) if post.category else None,
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
            form_data = form.cleaned_data
            ''' Create Permanent Item
            '''
            permanent_title = form_data['permanent']
            if PostPermanent.objects.filter(title=permanent_title).count() > 0:
                ''' When permanent title already exists
                '''
                post_permanent = PostPermanent.objects.get(title=permanent_title)
                if PostTranslate.objects.filter(permanent=post_permanent, language=get_language_from_request(request)).count() > 0:
                    raise BadRequest
                
            else:            
                post_permanent = PostPermanent()
                post_permanent.title = permanent_title
                post_permanent.save()
            ''' Create Post Item
            '''
            new_post = Post()
            new_post.title = form_data['title']
            new_post.permanent = post_permanent
            if (new_cover := request.FILES.get('cover')) is not None:
                fss = FileSystemStorage()
                cover_file = new_cover
                cover = fss.save(cover_file.name, cover_file)
                new_post.cover = cover
            new_post.date = form_data['date']
            category_name = form_data['category']
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
            new_post.content = form_data['content']
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
            ''' Create Post Translate
            '''
            new_translate = PostTranslate()
            new_translate.permanent = post_permanent
            new_translate.language = get_language_from_request(request)
            new_translate.post = new_post
            new_translate.save()
            return redirect(to='post_page', permanent_title=post_permanent.title)
        else:
            raise BadRequest


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
                'category': post.category.select_language(lang).name if post.category else None,
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
            raise BadRequest


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
            raise PermissionDenied


def user_logout(request: HttpRequest):
    if get_user(request).is_authenticated:
        logout(request)
    redirect_to = request.GET.get('redirect') or 'home'
    return redirect(to=redirect_to)


def pub_other_info(pub: Publication):
    base_info = f"{pub.publisher}"
    if pub.publication_type == 'article':
        if pub.volume:
            base_info += f", {pub.volume}"
        if pub.issue:
            base_info += f" ({pub.issue})"
        if pub.page_start and pub.page_end:
            base_info += f": {pub.page_start}-{pub.page_end}"
    else:
        if pub.page_start and pub.page_end:
            base_info += f": {pub.page_start}-{pub.page_end}"
    return base_info + "."


def publication_list(request: HttpRequest):
    pub_list = Publication.objects.order_by('-publish_date')
    if (query_year := request.GET.get('year')):
        pub_list = pub_list.filter(publish_date__year=query_year)
    pub_show_list = [{
        'id': pub.id,
        'title': pub.title,
        'authors': pub.authors,
        'cover': pub.cover,
        'publication_type': Publication.PublicationType(pub.publication_type).label,
        'year': pub.publish_date.year,
        'url': pub.url if pub.url is not None else '#',
        'other': pub_other_info(pub)
    } for pub in pub_list.all()]
    year_list = Publication.objects.values('publish_date__year').annotate(num_pub=Count('id')).order_by('-publish_date__year')
    return render(request, 'publication/list.html', {
        'publications': pub_show_list,
        'year_list': year_list
    })

def publication_page(request: HttpRequest, pub_id: int):
    pub = get_object_or_404(Publication, pk=pub_id)
    return render(request, 'publication/detail.html', {
        'publication': pub
    })
