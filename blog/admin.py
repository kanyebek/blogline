from django.contrib import admin
from .models import Post, SubPost


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ("title", "author", "created_at")
    search_fields = ("title", "content")
    list_filter = ("author", "created_at")
    ordering = ("-created_at",)


@admin.register(SubPost)
class SubPostAdmin(admin.ModelAdmin):
    model = SubPost
    list_display = ("title", "post", "created_at")
    search_fields = ("title",)
    list_filter = ("post", "created_at")
    ordering = ("-created_at",)


# Register your models here.
