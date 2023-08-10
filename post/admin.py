from django.contrib import admin
from .models import Post, PostLike, Comment, CommentLike


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'caption', 'created_time']
    search_fields = ['id', 'author__username']


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author','post_caption', 'created_time']
    search_fields = ['id', 'author__username']

    @admin.display(description='post_caption')
    def post_caption(self, obj):
        return obj.liked_post.caption[:30]


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author','body', 'post_caption', 'created_time']
    search_fields = ['id', 'author__username']

    @admin.display(description='post_caption')
    def post_caption(self, obj):
        return obj.comment_post.caption[:30]


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'comment_body', 'created_time']
    search_fields = ['id', 'author__username']

    @admin.display(description='comment_body')
    def comment_body(self, obj):
        return obj.liked_comment.body[:30]


admin.site.register(Post,PostAdmin)
admin.site.register(PostLike,PostLikeAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(CommentLike,CommentLikeAdmin)
