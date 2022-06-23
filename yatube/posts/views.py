from .paginator import paginate_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm


def index(request):
    """Shows latest posts on main page"""
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginate_page(request, post_list)
    return render(
        request,
        'posts/index.html',
        context={'page_obj': page_obj, }
    )


def group_posts(request, slug):
    """Shows posts which are related to the certain group"""
    group = get_object_or_404(Group, slug=slug)
    group_post_list = group.posts.select_related('author', 'group')
    page_obj = paginate_page(request, group_post_list)
    return render(
        request,
        'posts/group_list.html',
        context={'group': group,
                 'page_obj': page_obj, }
    )


def profile(request, username):
    """Shows posts which are related to the certain user"""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author', 'group')
    page_obj = paginate_page(request, post_list)
    if request.user.is_authenticated:
        if Follow.objects.filter(
                user=request.user,
                author=author).exists():
            return render(
                request,
                'posts/profile.html',
                context={
                    'author': author,
                    'page_obj': page_obj,
                    'following': True
                }
            )
    return render(
        request,
        'posts/profile.html',
        context={
            'author': author,
            'page_obj': page_obj,
        }
    )


def post_detail(request, post_id):
    """Shows one post and its author information"""
    post = get_object_or_404(Post, id=post_id)
    comments = reversed(post.comments.all())
    form = CommentForm(request.POST or None)
    return render(request,
                  'posts/post_detail.html',
                  context={
                      'form': form,
                      'post': post,
                      'comments': comments,
                      'user': request.user, })


@login_required
def post_create(request):
    """Shows form to create new post"""
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if not request.method == "POST":
        return render(request, "posts/create_post.html", {"form": form})
    if not form.is_valid():
        return render(request, "posts/create_post.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", request.user)


@login_required
def post_edit(request, post_id):
    """Shows form to edit and resave existing post"""
    posts = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=posts)
    context = {"form": form,
               "post": posts,
               "is_edit": True,
               }
    if not request.user == posts.author:
        return redirect("posts:post_detail", post_id)
    if not request.method == "POST":
        return render(request,
                      'posts/create_post.html',
                      context)
    if not form.is_valid():
        return render(request,
                      'posts/create_post.html',
                      context)
    form.save()
    return redirect("posts:post_detail", post_id)


@login_required
def add_comment(request, post_id):
    """Adds comment to a post"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    form.errors
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Shows posts only of authors the user is subscribed to"""
    authors_list = User.objects.filter(following__user=request.user)
    posts = Post.objects.filter(author__in=authors_list)
    page_obj = paginate_page(request, posts)
    return render(
        request,
        'posts/index.html',
        context={
            'page_obj': page_obj,
        }
    )


@login_required
def profile_follow(request, username):
    """Subscribe"""
    author = get_object_or_404(User, username=username)
    if (
        request.user != author
        and not Follow.objects.filter(
            user=request.user,
            author=author).exists()):
        Follow.objects.create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    """Unsubscribe"""
    author = get_object_or_404(User, username=username)
    if (
        request.user != author
        and Follow.objects.filter(
            user=request.user,
            author=author).exists()):
        Follow.objects.get(
            user=request.user,
            author=author
        ).delete()
    return redirect('posts:profile', username=author)
