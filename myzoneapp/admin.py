from django.contrib import admin
from django.db import models
from .models import Category, Post, Profile, Tag

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_en', 'name_zh_cn')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_en', 'name_zh_cn')


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Profile)