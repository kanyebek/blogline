from rest_framework import serializers
from django.db import transaction
from .models import Post, SubPost


class SubPostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = SubPost
        fields = ("id", "title", "body", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")


class PostSerializer(serializers.ModelSerializer):
    subposts = SubPostSerializer(many=True, required=False)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "body",
            "author",
            "created_at",
            "updated_at",
            "subposts",
            "likes_count",
            "views_count",
        )
        read_only_fields = ("created_at", "updated_at", "views_count", "likes_count")

    def create(self, validated_data):
        subposts_data = validated_data.pop("subposts", [])
        with transaction.atomic():
            post = Post.objects.create(**validated_data)
            for sub in subposts_data:
                SubPost.objects.create(post=post, **sub)
        return post

    def update(self, instance, validated_data):
        subposts_data = validated_data.pop("subposts", None)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if subposts_data is not None:
                existing_ids = [s.id for s in instance.subposts.all()]
                incoming_ids = [s.get("id") for s in subposts_data if s.get("id")]

                for s_data in subposts_data:
                    s_id = s_data.get("id")
                    if s_id:
                        SubPost.objects.filter(id=s_id, post=instance).update(
                            title=s_data.get("title", ""), body=s_data.get("body", "")
                        )
                    else:
                        SubPost.objects.create(post=instance, **s_data)

                to_delete = [sid for sid in existing_ids if sid not in incoming_ids]
                if to_delete:
                    SubPost.objects.filter(id__in=to_delete).delete()
        return instance
