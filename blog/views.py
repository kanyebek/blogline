from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import F
from .models import Post, SubPost
from .serializers import PostSerializer, SubPostSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return (
            Post.objects.prefetch_related("subposts", "likes")
            .all()
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        return {"request": self.request}

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        if isinstance(serializer.validated_data, list):
            for item in serializer.validated_data:
                if "author" not in item:
                    item["author"] = self.request.user
            serializer.save()
        else:
            if "author" not in serializer.validated_data:
                serializer.validated_data["author"] = self.request.user
            serializer.save()

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if post.likes.filter(pk=user.pk).exists():
            post.likes.remove(user)
            return Response({"liked": False, "likes_count": post.likes.count()})
        else:
            post.likes.add(user)
            return Response({"liked": True, "likes_count": post.likes.count()})

    @action(detail=True, methods=["get"])
    def view(self, request, pk=None):
        post = self.get_object()
        Post.objects.filter(pk=post.pk).update(views_count=F("views_count") + 1)
        post.refresh_from_db()
        return Response({"views_count": post.views_count})


class SubPostViewSet(viewsets.ModelViewSet):
    queryset = SubPost.objects.all().order_by("-created_at")
    serializer_class = SubPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()
