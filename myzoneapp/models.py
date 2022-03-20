from email.policy import default
from django.db import models
from vditor.fields import VditorTextField
from myzone.settings import MEDIA_ROOT
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self) -> str:
        return f"{self.name}"


class Tag(models.Model):
    name = models.CharField(max_length=15)

    def __str__(self) -> str:
        return f"{self.name}"


class Post(models.Model):
    title = models.CharField(max_length=255)
    cover = models.ImageField(upload_to='covers', null=True, blank=True)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    draft = models.BooleanField(default=False)
    content = VditorTextField(default='')

    def __str__(self) -> str:
        return f"{self.title} | {self.date}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
    content = VditorTextField(default='')
