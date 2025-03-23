from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from . models import BlogPost, Comment, PostLike, Tag
from .forms import CommentForm, ReplyForm, PostCreationForm
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Q
from account.models import ProfileUser
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache


class HomeView(ListView):
    """
    A view for displaying the homepage that includes a list of blog posts, approved comments count,
    user profile, and top liked and tagged posts.

    Model: BlogPost
    Template: 'core/home.html'
    Context Object Name: 'obj'
    Items per Page: 5
    """
    model = BlogPost
    template_name = 'core/home.html'
    context_object_name = 'obj'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        """
        Adds additional data to the context, such as approved comments, user profile, top liked posts,
        and top tags. It also uses caching to improve performance and reduce database queries.

        Caches are used for storing approved comments, user profiles, top liked posts, and top tags
        to improve website performance by reducing server load.
        """
        # Get the default context from the parent class (ListView)
        context = super().get_context_data(**kwargs)
        comments_cache_key = 'approved_comments_per_post'
        comments = cache.get(comments_cache_key)

        # If comments are not in the cache, retrieve them from the database
        if not comments:
            comments = BlogPost.objects.annotate(
                approved_comments=Count('comments', filter=Q(comments__is_approved=True))
            ).values('id', 'approved_comments')
            cache.set(comments_cache_key, comments, timeout=1200)

        comment_dict = {item['id']: item['approved_comments'] for item in comments}

        for post in context['obj']:
            post.approved_comments = comment_dict.get(post.id, 0)

        # Cache key for storing the user profile
        profile_cache_key = f"profile_{self.request.user.id}"
        profile = cache.get(profile_cache_key)

        # If the profile is not in the cache, retrieve it from the database
        if profile is None:
            try:
                profile = ProfileUser.objects.get(user=self.request.user.id)
                cache.set(profile_cache_key, profile, timeout=43200)
            except ProfileUser.DoesNotExist:
                profile = None
                cache.set(profile_cache_key, profile, timeout=43200)

        context['profile'] = profile

        # Cache key for storing the top liked posts
        top_liked_posts = cache.get('top_liked_posts')

        # If top liked posts are not in the cache, retrieve them from the database
        if not top_liked_posts:
            top_liked_posts = BlogPost.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:4]
            cache.set('top_liked_posts', top_liked_posts, timeout=21600)
        context['top_liked_posts'] = top_liked_posts

        # Cache key for storing the top tagged posts
        top_tags_posts = cache.get('top_tags_posts')

        # If top tagged posts are not in the cache, retrieve them from the database
        if not top_tags_posts:
            top_tags_posts = Tag.objects.annotate(post_count=Count('blogpost')).order_by('-post_count')
            cache.set('top_tags_posts', top_tags_posts, timeout=21600)
        context['top_tags_posts'] = top_tags_posts

        return context


class BlogPostDetailView(DetailView):
    """
    View for displaying the details of a single blog post.
    Handles fetching post details, caching approved comments, top liked posts,
    and processing user interactions such as liking or commenting on the post.
    """
    model = BlogPost
    template_name = 'core/post-detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """
        Adds extra context data including cached approved comments,
        a comment form, a reply form, top liked posts, and like status.
        """
        context = super().get_context_data(**kwargs)

        post_id = self.object.id
        approved_comments_cache_key = f'approved_comments_{post_id}'
        approved_comments = cache.get(approved_comments_cache_key)

        # Cache approved comments to reduce database queries
        if not approved_comments:
            approved_comments = list(self.object.comments.filter(is_approved=True))
            cache.set(approved_comments_cache_key, approved_comments, timeout=1200)
        context['comments'] = approved_comments

        context['comment_form'] = CommentForm()
        context['reply_form'] = ReplyForm

        # Cache top 4 most liked posts to improve performance
        top_liked_posts_cache_key = 'top_liked_posts'
        top_liked_posts = cache.get(top_liked_posts_cache_key)

        if not top_liked_posts:
            top_liked_posts = list(BlogPost.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:4])
            cache.set(top_liked_posts_cache_key, top_liked_posts, timeout=21600)
        context['top_liked_posts'] = top_liked_posts

        # Check if the current user has liked this post (cached for performance)
        user = self.request.user
        context['is_liked'] = False
        if user.is_authenticated:
            user_like_cache_key = f'user_like_{user.id}_liked_post_{post_id}'
            is_liked = cache.get(user_like_cache_key)
            if is_liked is None:
                # If the like status is not cached, query the database and cache the result
                is_liked = PostLike.objects.filter(user=self.request.user, post=post_id).exists()
                cache.set(user_like_cache_key, is_liked, timeout=3600)
            context['is_liked'] = is_liked

        return context

    def post(self, request, *args, **kwargs):
        """
        Handles form submissions for adding or editing comments.
        Ensures only authenticated users can post comments and updates the cache accordingly.
        """
        self.object = self.get_object()

        # Handle new comment submission
        if 'new_comment' in request.POST:
            form = CommentForm(request.POST)
            if request.user.is_authenticated:
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.post = self.object
                    comment.user = request.user
                    comment.save()

                    # Clear cache to ensure updated comments are fetched
                    cache.delete(f"approved_comments_{self.object.id}")

                    messages.success(request,
                                     'Your comment will be displayed after it is approved by the administrator.')
                    return redirect(reverse('core:post-detail', args=[self.object.pk, self.object.slug]))

                messages.error(request, 'Something went wrong')
                return self.render_to_response(self.get_context_data(comment_form=form))

            messages.info(request, 'Please login first')
            return redirect(reverse('core:post-detail', args=[self.object.pk, self.object.slug]))

        # Handle editing an existing comment
        if 'edit_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()

                # Clear cache to ensure updated comments are reflected
                cache.delete(f"approved_comments_{self.object.id}")

                messages.success(request, 'Your comment was successfully edited!')
                return redirect('core:post-detail', pk=self.object.pk, slug=self.object.slug)

            context = self.get_context_data()
            context['comment_form'] = form
            return self.render_to_response(context)


class ReplyCommentView(View):
    """
    Handles replies to comments on a blog post.
    Allows authenticated users to submit replies and edit their own replies.
    """
    form_class = ReplyForm

    def post(self, request, post_id, comment_id):
        """
        Processes reply submissions and edits to existing replies.
        """
        post = get_object_or_404(BlogPost, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id)

        # Handle reply editing
        if 'edit_reply' in request.POST:
            reply_id = request.POST.get('reply_id')
            reply = get_object_or_404(Comment, id=reply_id, reply=comment)

            if request.user == reply.user:
                form = self.form_class(request.POST, instance=reply)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Your reply has been successfully updated.')
                else:
                    messages.error(request, 'Something went wrong with your reply update.')
            else:
                messages.error(request, 'You are not authorized to edit this reply.')

            return redirect('core:post-detail', pk=post.pk, slug=post.slug)

        # Handle new reply submission
        if request.user.is_authenticated:
            form = self.form_class(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.user = request.user
                reply.post = post
                reply.reply = comment  # Assign reply to the correct comment
                reply.is_reply = True
                reply.save()
                messages.success(request, 'Your reply submitted successfully.')
            else:
                messages.error(request, 'Something went wrong!')

            return redirect('core:post-detail', pk=post.pk, slug=post.slug)

        messages.info(request, 'Please login first!')
        return redirect('core:post-detail', pk=post.pk, slug=post.slug)


class DeleteReplyView(View):
    """Allows an authenticated user to delete their own reply."""
    def get(self, request, reply_id):
        reply = get_object_or_404(Comment, id=reply_id, is_reply=True)
        if request.user.is_authenticated and reply.user == request.user:
            cache.delete(f"approved_comments_{reply.post.id}")
            reply.delete()
            messages.success(request, 'Your reply has been successfully deleted.')
            return redirect('core:post-detail', pk=reply.post.pk, slug=reply.post.slug)

        messages.error(request, 'You are not authorized to delete this reply.')
        return redirect('core:post-detail', pk=reply.post.pk, slug=reply.post.slug)

class DeleteCommentView(View):
    """Allows a user to delete their own comment from a post."""
    def get(self,  request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user == request.user:
            cache.delete(f"approved_comments_{comment.post.id}")
            comment.delete()
            messages.success(request, 'Your comment has been deleted successfully.')
            return redirect('core:post-detail', pk=comment.post.id, slug=comment.post.slug)
        return redirect('core:post-detail', pk=comment.post.id, slug=comment.post.slug)


class LikePostView(View):
    """
    Handles liking and unliking a blog post.
    Users must be authenticated to like a post. If the user has already liked the post,
    the like is removed (unlike); otherwise, a new like is created.
    """

    def post(self, request, pk, slug):
        post = get_object_or_404(BlogPost, pk=pk, slug=slug)

        if not request.user.is_authenticated:
            messages.info(request, 'Please login to like this post.')
            return redirect('core:post-detail', pk=post.pk, slug=post.slug)

        existing_like = PostLike.objects.filter(user=request.user, post=post)

        if existing_like.exists():
            # If the user has already liked the post, remove the like
            existing_like.delete()
            messages.success(request, 'You have unliked this post.')
        else:
            # Otherwise, create a new like
            PostLike.objects.create(user=request.user, post=post)
            messages.success(request, 'You have liked this post.')

        return redirect('core:post-detail', pk=post.pk, slug=post.slug)


class PostCreationView(UserPassesTestMixin, View):
    """
    Handles blog post creation and editing.
    Only superusers can create or edit posts.
    """
    template_name = 'core/post-creation.html'
    from_class = PostCreationForm
    tags = Tag.objects.all()

    def test_func(self):
        """Ensures only superusers can access this view."""
        return self.request.user.is_superuser

    def get(self, request, pk=None):
        """
        Displays the post creation form. If `pk` is provided, loads an existing post for editing.
        """
        if pk:
            post = get_object_or_404(BlogPost, pk=pk)
            form = self.from_class(instance=post)
            return render(request, self.template_name, {'form': form, 'tags': self.tags, 'post': post})
        else:
            form = self.from_class()
            return render(request, self.template_name, {'form': form, 'tags': self.tags})

    def post(self, request, pk=None):
        """
        Handles post submission. Creates a new post or updates an existing one.
        """
        if pk:
            post = get_object_or_404(BlogPost, pk=pk)
            form = self.from_class(request.POST, request.FILES, instance=post)
        else:
            form = self.from_class(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            post = form.save(commit=False)
            post.cover_image = request.FILES.get('cropped_image', cd['cover_image'])  # Handle cover image
            post.save()
            post.tags.set(cd['tags'])  # Assign tags to the post

            messages.success(request,
                             'The post was updated successfully' if pk else 'The post was created successfully')
            return redirect('core:home') if not pk else redirect('core:post-detail', pk=post.pk, slug=post.slug)

        messages.error(request, 'Please enter valid information')
        return render(request, self.template_name, {'form': form, 'tags': self.tags})


class PostsShowView(ListView):
    """
    Displays a list of blog posts with optional search functionality.
    Retrieves comment and like counts using caching for better performance.
    """
    model = BlogPost
    template_name = 'core/posts.html'
    context_object_name = 'obj'

    def get_queryset(self):
        """Retrieves all blog posts and filters them based on the search query if provided."""
        queryset = BlogPost.objects.all()
        query = self.request.GET.get('q', None)

        if query:
            queryset = queryset.filter(Q(title_heading__icontains=query) | Q(title_description__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        """Adds comment and like counts to each blog post in the context."""
        context = super().get_context_data(**kwargs)

        comments_cache_key = 'approved_comments'
        comments = cache.get(comments_cache_key)

        if not comments:
            comments = BlogPost.objects.annotate(
                approved_comments=Count('comments', filter=Q(comments__is_approved=True))
            ).values('id', 'approved_comments')
            cache.set(comments_cache_key, comments, timeout=1200)

        comment_dict = {item['id']: item['approved_comments'] for item in comments}

        likes_cache_key = 'post_like'
        likes = cache.get(likes_cache_key)

        if not likes:
            likes = BlogPost.objects.annotate(like_count=Count('likes')).values('id', 'like_count')
            cache.set(likes_cache_key, likes, timeout=1200)

        like_dict = {item['id']: item['like_count'] for item in likes}

        for post in context['obj']:
            post.approved_comments = comment_dict.get(post.id, 0)
            post.like_count = like_dict.get(post.id, 0)

        context['query'] = self.request.GET.get('q', '')

        return context


class DeletePostView(UserPassesTestMixin, View):
    """Handles the deletion of a blog post by an admin user."""
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, pk):
        """Deletes the selected post and redirects to the post list."""
        post = get_object_or_404(BlogPost, pk=pk)
        post.delete()
        messages.success(request, 'The post was deleted successfully.')
        return redirect('core:posts')
