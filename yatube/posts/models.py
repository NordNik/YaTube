from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Post(models.Model):
    text = models.TextField(help_text="Enter or edit your post's text")
    pub_date = models.DateTimeField(db_index=True,
                                    auto_now_add=True,
                                    verbose_name="PublicationDate")
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text="Related group"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return f'Группа "{self.title}"'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(help_text="Comment post here")
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name="CommentDate")

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique user-author pair'
            )
        ]
        verbose_name = 'Subscriptions'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.user}'


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    liked_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'liked_user'],
                name='unique post-liked_user pair'
            )
        ]
        verbose_name = 'Likes'
        verbose_name_plural = 'Likes'


class Dislike(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='dislikes'
    )
    disliked_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dislikes'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'disliked_user'],
                name='unique post-disliked_user pair'
            )
        ]
        verbose_name = 'Dislikes'
        verbose_name_plural = 'Dislikes'
