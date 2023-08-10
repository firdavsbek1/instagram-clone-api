from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Post, User, PostLike, Comment, CommentLike


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'photo']


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField('get_comments_count')
    likes_count = serializers.SerializerMethodField('get_likes_count')
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = Post
        fields = ['id', 'author', 'post_image', 'caption', 'created_time',
                  'likes_count', 'comments_count', 'me_liked'
                  ]
        extra_kwargs={
            'post_image':{"required":False}
        }

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_me_liked(self, obj):
        request = self.context.get('request')
        user = request.user
        if user and user.is_authenticated:
            try:
                PostLike.objects.get(author=user, liked_post=obj)
                return True
            except PostLike.DoesNotExist:
                pass
        return False


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField("get_replies_count")
    likes_count = serializers.SerializerMethodField("get_likes_count")
    me_liked = serializers.SerializerMethodField("get_me_liked")
    replies = serializers.SerializerMethodField('get_replies')

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'body', 'parent', 'created_time', 'replies_count', 'likes_count', 'me_liked', 'replies'
        ]

    def get_replies(self, obj):
        if obj.replies.exists():
            serializer = self.__class__(context=self.context, instance=obj.replies.all(), many=True)
            return serializer.data
        return None

    def get_replies_count(self, obj):
        return obj.replies.count()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_me_liked(self, obj):
        request = self.context.get('request')
        user = request.user
        if user and user.is_authenticated:
            if CommentLike.objects.filter(author=user, liked_comment=obj).exists():
                return True
        return False


class PostLikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    liked_post = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PostLike
        fields = [
            'id', 'author', 'liked_post'
        ]


class CommentLikeSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True)
    author=serializers.StringRelatedField(read_only=True)
    liked_comment=serializers.StringRelatedField(read_only=True)

    class Meta:
        model= CommentLike
        fields=[
            'id','author','liked_comment'
        ]