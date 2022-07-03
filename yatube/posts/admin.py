from django.contrib import admin
from .models import Post, Group, Comment, Follow, Like, Dislike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('description',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'post', 'author', 'created')
    search_fields = ('author',)
    search_fields = ('post',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    empty_value_display = '-пусто-'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'liked_user')
    empty_value_display = '-пусто-'


@admin.register(Dislike)
class DisikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'disliked_user')
    empty_value_display = '-пусто-'
