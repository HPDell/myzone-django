from django.db import models
from vditor.fields import VditorTextField

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
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, null=True)
    content = VditorTextField(default='')

    def __str__(self) -> str:
        return f"{self.title} | {self.date}"
