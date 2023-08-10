from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

from shared.models import BaseModel
from django.core.validators import FileExtensionValidator,MaxLengthValidator

User=get_user_model()


class Post(BaseModel):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name='posts')
    post_image=models.ImageField(verbose_name='Post Image',upload_to='posts/images/',validators=[
        FileExtensionValidator(allowed_extensions=['jpeg','jpg','jfif','heif','png','avif'])
    ],null=False)
    caption=models.TextField(validators=[MaxLengthValidator(1000)])

    class Meta:
        db_table='posts'
        verbose_name='post'
        verbose_name_plural='posts'

    def __str__(self):
        return self.caption


class Comment(BaseModel):
    author=models.ForeignKey(User,on_delete=models.SET_NULL,related_name='comments',null=True,blank=True)
    comment_post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    body=models.TextField(validators=[MaxLengthValidator(500)])
    parent=models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='replies',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.body


class PostLike(BaseModel):
    author=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    liked_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints=[
            UniqueConstraint(
                name="OneLikePerUserPerPost",
                fields=['author','liked_post']
            )
        ]

    def __str__(self):
        return f"post({self.liked_post.caption[:20]}) liked by {self.author}"


class CommentLike(BaseModel):
    author=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    liked_comment=models.ForeignKey(Comment,on_delete=models.CASCADE,related_name='likes')

    class Meta:
        constraints=[
            UniqueConstraint(
                name='OneLikePerUserPerComment',
                fields=['author','liked_comment']
            )
        ]

    def __str__(self):
        return f"comment({self.liked_comment.body[:20]}) liked by {self.author}"

