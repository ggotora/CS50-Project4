from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass 

class Comment(models.Model):
    content = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    content = models.TextField(verbose_name='')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, blank=True, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="post_like", blank=True)
