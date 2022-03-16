from django.contrib import admin
from django.db import models
from .models import Category, Post, Tag
from vditor.widgets import VditorWidget

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)