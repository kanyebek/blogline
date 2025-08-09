from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class SubPost(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="subposts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.post_id} - {self.title}"
