from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from .models import Post, Comment, PostLike, CommentLike
from .serializers import PostSerializer, CommentSerializer,PostLikeSerializer,CommentLikeSerializer

from rest_framework import permissions, status
from shared.custom_pagination import CustomPagination
from shared.custom_permissions import IsAdminIsOwnerOrReadOnly
from rest_framework.response import Response


class PostListAPIView(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAdminIsOwnerOrReadOnly, ]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                'success': True,
                'message': "You post has been deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT
        )


class PostCommentListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        post = Post.objects.filter(id=self.kwargs['pk']).first()
        return post.comments


class PostCommentListCreateAPIView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Comment.objects.all()
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, comment_post_id=self.request.data.get('post_id'),
                        parent_id=self.request.data.get('parent_id'))


class PostLikeListAPIView(ListCreateAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]

    def get_queryset(self):
        liked_post_id=self.request.data.get('liked_post')
        return PostLike.objects.filter(liked_post_id=liked_post_id)

    def perform_create(self, serializer):
        liked_post_id=self.request.data.get('liked_post')
        try:
            like=PostLike.objects.get(author=self.request.user,liked_post_id=liked_post_id)
            like.delete()
        except PostLike.DoesNotExist:
            serializer.save(author=self.request.user,liked_post_id=liked_post_id)
        except Exception:
            raise ValidationError(
                {
                    'success': False,
                    'message': "The post id is not valid!"
                }
            )

    # def post(self, request, *args, **kwargs):
    #     data=self.perform_create(self.serializer_class)
    #     print(data)
    #     serialized_data=super().post(request,*args,**kwargs).data
    #     print(data,serialized_data)
    #     if data:
    #         return Response({'success':True,'data':data},status=status.HTTP_204_NO_CONTENT)
    #     return Response({'success':True,'data':serialized_data},status=status.HTTP_201_CREATED)


class CommentLikeListAPIView(ListCreateAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]

    def get_queryset(self):
        liked_comment_id=self.request.data.get('liked_comment')
        return CommentLike.objects.filter(liked_comment_id=liked_comment_id)

    def perform_create(self, serializer):
        liked_comment_id=self.request.data.get('liked_comment')
        try:
            like=CommentLike.objects.get(author=self.request.user,liked_comment_id=liked_comment_id)
            print(like)
            like.delete()
        except CommentLike.DoesNotExist:
            serializer.save(author=self.request.user,liked_comment_id=liked_comment_id)
        except Exception as x:
            raise ValidationError(
                {
                    'success': False,
                    'message': "The comment id is not valid!"
                }
            )

