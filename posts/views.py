from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    posts = Post.objects.order_by('-pub_date')

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html', {
        'page': page,
        'paginator': paginator,
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date")

    paginator = Paginator(posts, 5)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'group.html', {
        'group': group,
        'paginator': paginator,
        'page': page,
    })


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})

    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = Post.objects.filter(author=author).count()
    author_posts = Post.objects.filter(author=author).order_by('-pub_date')
    followers_count = author.following.count()
    following_count = author.follower.count()

    following = False
    if request.user.is_authenticated:
        if request.user.username == username:
            following = 'Self'
        if Follow.objects.filter(user=request.user).filter(author=author):
            following = True

    paginator = Paginator(author_posts, 6)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'profile.html', {
        'page': page,
        'paginator': paginator,
        'posts_count': posts_count,
        'author': author,
        'following': following,
        'following_count': following_count,
        'followers_count': followers_count
    })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author.id, id=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    comments = Comment.objects.filter(post=post)
    followers_count = author.following.count()
    following_count = author.follower.count()

    return render(request, 'post.html', {
        'posts_count': posts_count,
        'post': post,
        'form': CommentForm(),
        'comments': comments,
        'author': author,
        'followers_count': followers_count,
        'following_count': following_count
    })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return post_view(request, username, post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    form_content = {'form': form, 'post': post, 'post_edit': True}

    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('post', username=post.author, post_id=post.id)
        return render(request, 'new.html', form_content)

    return render(request, "new.html", form_content)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(
                'post', username=post.author.username, post_id=post.id
            )

    form = CommentForm()
    return redirect('post', username=post.author.username, post_id=post.id)


@login_required
def post_delete(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('post', username=post.author.username, post_id=post_id)

    post.delete()

    return redirect('profile', username=post.author.username)


@login_required
def follow_index(request):
    posts = Post.objects.order_by('-pub_date').filter(
        author__following__user=request.user
    )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'follow.html', {
        'page': page,
        'paginator': paginator,
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author.username != request.user.username:
        if Follow.objects.filter(user=request.user).filter(author=author):
            return redirect('index')

        followers = Follow(user=request.user, author=author)
        followers.save()

    return redirect('index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    followers = Follow.objects.get(user=request.user, author=author)
    followers.delete()

    return redirect('index')
