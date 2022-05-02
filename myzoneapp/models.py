from email.policy import default
from tkinter.tix import Balloon
from typing import Union
from django.db import models
from vditor.fields import VditorTextField
from myzone.settings import MEDIA_ROOT, LANGUAGES
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from sorl.thumbnail import ImageField as ThumbImageField

# Create your models here.

class MultilingualQuerySet(models.query.QuerySet):
    selected_language = None

    def __init__(self, *args, **kwargs):
        super(MultilingualQuerySet, self).__init__(*args, **kwargs)

    def select_language(self, lang):
        self.selected_language = lang
        return self

    def iterator(self):
        result_iter = super(MultilingualQuerySet, self).iterator()
        for result in result_iter:
            if hasattr(result, 'select_language'):
                result.select_language(self.selected_language)
            yield result

    def _clone(self, *args, **kwargs):
        qs = super(MultilingualQuerySet, self)._clone(*args, **kwargs)
        if hasattr(qs, 'select_language'):
            qs.select_language(self.selected_language)
        return qs


class MultilingualManager(models.Manager):
    use_for_related_fields = True
    selected_language = None

    def select_language(self, lang):
        self.selected_language = lang
        return self

    def get_query_set(self):
        qs = MultilingualQuerySet(self.model, using=self._db)
        return qs.select_language(self.selected_language)


class MultilingualModel(models.Model):
    # fallback/default language code
    default_language = LANGUAGES[0][0]

    # currently selected language
    selected_language: Union[None, str] = None

    objects = MultilingualManager()

    class Meta:
        abstract = True
        default_manager_name = 'objects'

    def select_language(self, lang):
        """Select a language"""
        self.selected_language = lang
        return self

    def __getattribute__(self, name):
        def get(x):
            return super(MultilingualModel, self).__getattribute__(x)

        try:
            # Try to get the original field, if exists
            value = get(name)
            # If we can select language on the field as well, do it
            if isinstance(value, MultilingualModel):
                value.select_language(get('selected_language'))
            return value
        except AttributeError as e:
            # Try the translated variant, falling back to default if no
            # language has been explicitly selected
            lang = self.selected_language
            if not lang:
                lang = self.default_language
            if not lang:
                raise

            value = get(name + '_' + lang)

            # If the translated variant is empty, fallback to default
            if isinstance(value, str) and value == u'':
                value = get(name + '_' + self.default_language)

        return value


class Category(MultilingualModel):
    name_en = models.CharField(max_length=15, default='', blank=True)
    name_zh_cn = models.CharField(max_length=15, default='', blank=True)

    def __str__(self) -> str:
        return f"{self.name}"


class Tag(MultilingualModel):
    name_en = models.CharField(max_length=15, default='', blank=True)
    name_zh_cn = models.CharField(max_length=15, default='', blank=True)

    def __str__(self) -> str:
        return f"{self.name}"


class Post(models.Model):
    title = models.CharField(max_length=255)
    cover = ThumbImageField(upload_to='covers', null=True, blank=True)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    draft = models.BooleanField(default=False)
    content = VditorTextField(default='')

    def __str__(self) -> str:
        return f"{self.title} | {self.date}"


class Profile(MultilingualModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
    content_en = VditorTextField(default='')
    content_zh_cn = VditorTextField(default='')


class Publication(models.Model):
    
    class PublicationType(models.TextChoices):
        ARTICLE = 'article', _('Journal Article')
        BOOK = 'book', _('Book (Chapter)')
        CONFERENCE = 'conference', _('Conference Proceeding')

        __empty__ = _('Unknown')

    title = models.CharField(max_length=255)
    publication_type = models.CharField(max_length=10, choices=PublicationType.choices, default=PublicationType.ARTICLE)
    authors = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    cover = ThumbImageField(upload_to='publication_covers', null=True, blank=True)
    publish_date = models.DateField(null=True, blank=True)
    volume = models.PositiveSmallIntegerField(null=True, blank=True)
    issue = models.PositiveSmallIntegerField(null=True, blank=True)
    edition = models.PositiveSmallIntegerField(null=True, blank=True)
    page_start = models.PositiveIntegerField(null=True, blank=True)
    page_end = models.PositiveIntegerField(null=True, blank=True)
    doi = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    abstract = VditorTextField(default='')
