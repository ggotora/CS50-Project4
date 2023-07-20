from django.contrib.auth.models import AbstractUser
from django.db import models

from django.db.models.signals import post_save


class User(AbstractUser):
    pass 

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField('self', related_name="followed_by", symmetrical=False, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} Profile"
    
    def create_profile(sender, instance, created, **kwargs):
        if created:
            user_profile = Profile(user=instance)
            user_profile.save()
    post_save.connect(create_profile, sender=User)

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

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self) -> str:
        return f"{self.content[:15]} ..."
    
