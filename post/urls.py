from django.urls import path
import post.views as views

urlpatterns=[
    path("",views.PostListAPIView.as_view()),
    path("post/likes/",views.PostLikeListAPIView.as_view()),
    path("comment/likes/",views.CommentLikeListAPIView.as_view()),
    path("<uuid:pk>/",views.PostRetrieveUpdateDeleteAPIView.as_view()),
    path("<uuid:pk>/comments/",views.PostCommentListAPIView.as_view()),
    path("comments/",views.PostCommentListCreateAPIView.as_view()),
]