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
    model = BlogPost
    template_name = 'core/home.html'
    context_object_name = 'obj'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments_cache_key = 'approved_comments_per_post'
        comments = cache.get(comments_cache_key)

        if not comments:
            comments = BlogPost.objects.annotate(
                approved_comments=Count('comments', filter=Q(comments__is_approved=True))
            ).values('id', 'approved_comments')
            cache.set(comments_cache_key, comments, timeout=1200)

        comment_dict = {item['id']: item['approved_comments'] for item in comments}

        for post in context['obj']:
            post.approved_comments = comment_dict.get(post.id, 0)

        profile_cache_key = f"profile_{self.request.user.id}"
        profile = cache.get(profile_cache_key)

        if profile is None:
            try:
                profile = ProfileUser.objects.get(user=self.request.user.id)
                cache.set(profile_cache_key, profile, timeout=43200)
            except ProfileUser.DoesNotExist:
                profile = None
                cache.set(profile_cache_key, profile, timeout=43200)

        context['profile'] = profile

        top_liked_posts = cache.get('top_liked_posts')
        if not top_liked_posts:
            top_liked_posts = BlogPost.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:4]
            cache.set('top_liked_posts', top_liked_posts, timeout=21600)
        context['top_liked_posts'] = top_liked_posts

        top_tags_posts = cache.get('top_tags_posts')
        if not top_tags_posts:
            top_tags_posts = Tag.objects.annotate(post_count=Count('blogpost')).order_by('-post_count')
            cache.set('top_tags_posts', top_tags_posts, timeout=21600)
        context['top_tags_posts'] = top_tags_posts

        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'core/post-detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post_id = self.object.id
        approved_comments_cache_key = f'approved_comments_{post_id}'
        approved_comments = cache.get(approved_comments_cache_key)

        if not approved_comments:
            approved_comments = list(self.object.comments.filter(is_approved=True))
            cache.set(approved_comments_cache_key, approved_comments, timeout=1200)
        context['comments'] = approved_comments

        context['comment_form'] = CommentForm()
        context['reply_form'] = ReplyForm

        top_liked_posts_cache_key = 'top_liked_posts'
        top_liked_posts = cache.get(top_liked_posts_cache_key)

        if not top_liked_posts:
            top_liked_posts = BlogPost.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:4]
            cache.set(top_liked_posts_cache_key, top_liked_posts, timeout=21600)
        context['top_liked_posts'] = top_liked_posts

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'new_comment' in request.POST:
            form = CommentForm(request.POST)
            if request.user.is_authenticated:
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.post = self.object
                    comment.user = request.user
                    comment.save()

                    cache.delete(f"approved_comments_{self.object.id}")

                    messages.success(request, 'Your comment will be displayed after it is approved by the administrator'
                                              '.')
                    return redirect(reverse('core:post-detail', args=[self.object.pk, self.object.slug]))
                messages.error(request, 'Somthing went Wrong')
                return self.render_to_response(self.get_context_data(comment_form=form))
            messages.info(request, 'Please login first')
            return redirect(reverse('core:post-detail', args=[self.object.pk, self.object.slug]))

        if 'edit_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                form.save()

                cache.delete(f"approved_comments_{self.object.id}")

                messages.success(request, 'your comment was successfully edit!')
                return redirect('core:post-detail', pk=self.object.pk, slug=self.object.slug)
            context = self.get_context_data()
            context['comment_form'] = form
            return self.render_to_response(context)


class ReplyCommentView(View):
    form_class = ReplyForm

    def post(self, request, post_id, comment_id):
        post = get_object_or_404(BlogPost, id=post_id)
        comment = get_object_or_404(Comment, id=comment_id)

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

        if request.user.is_authenticated:
            form = self.form_class(request.POST)
            if form.is_valid():
                reply = form.save(commit=False)
                reply.user = request.user
                reply.post = post
                reply.reply = comment
                reply.is_reply = True
                reply.save()
                messages.success(request, 'Your reply submitted successfully.')
            else:
                messages.error(request, 'Something went wrong!')

            return redirect('core:post-detail', pk=post.pk, slug=post.slug)

        messages.info(request, 'Please login first!')
        return redirect('core:post-detail', pk=post.pk, slug=post.slug)


class DeleteReplyView(View):
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
    def get(self,  request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user == request.user:
            cache.delete(f"approved_comments_{comment.post.id}")
            comment.delete()
            messages.success(request, 'Your comment has been deleted successfully.')
            return redirect('core:post-detail', pk=comment.post.id, slug=comment.post.slug)
        return redirect('core:post-detail', pk=comment.post.id, slug=comment.post.slug)


class LikePostView(View):
    def post(self, request, pk, slug):
        post = get_object_or_404(BlogPost, pk=pk, slug=slug)
        if not request.user.is_authenticated:
            messages.info(request, 'Please login to like this post.')
            return redirect('core:post-detail', pk=post.pk, slug=post.slug)

        existing_like = PostLike.objects.filter(user=request.user, post=post).delete()

        # if existing_like.exists():
        if existing_like[0] > 0:
            # existing_like.delete()
            messages.success(request, 'You have unliked this post.')
        else:
            PostLike.objects.create(user=request.user, post=post)
            messages.success(request, 'You have liked this post.')
        return redirect('core:post-detail', pk=post.pk, slug=post.slug)


class PostCreationView(UserPassesTestMixin, View):
    template_name = 'core/post-creation.html'
    from_class = PostCreationForm
    tags = Tag.objects.all()

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, pk=None):
        if pk:
            post = get_object_or_404(BlogPost, pk=pk)
            form = self.from_class(instance=post)
            return render(request, self.template_name, {'form': form, 'tags': self.tags, 'post': post})
        else:
            form = self.from_class()
            return render(request, self.template_name, {'form': form, 'tags': self.tags})

    def post(self, request, pk=None):
        if pk:
            post = get_object_or_404(BlogPost, pk=pk)
            form = self.from_class(request.POST, request.FILES, instance=post)
        else:
            form = self.from_class(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            post = form.save(commit=False)
            post.cover_image = request.FILES.get('cropped_image', cd['cover_image'])
            post.save()
            post.tags.set(cd['tags'])

            messages.success(request,
                             'The post was updated successfully' if pk else 'The post was created successfully')
            return redirect('core:home') if not pk else redirect('core:post-detail', pk=post.pk, slug=post.slug)
        messages.error(request, 'Please Enter valid information')
        return render(request, self.template_name, {'form': form, 'tags': self.tags})


class PostsShowView(ListView):
    model = BlogPost
    template_name = 'core/posts.html'
    context_object_name = 'obj'

    def get_queryset(self):
        queryset = BlogPost.objects.all()
        query = self.request.GET.get('q', None)

        if query:
            queryset = queryset.filter(Q(title_heading__icontains=query) | Q(title_description__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments_cache_key = 'approved_comments'
        comments = cache.get(comments_cache_key)

        if not comments:
            comments = BlogPost.objects.annotate(
                approved_comments=Count('comments', filter=Q(comments__is_approved=True))
            ).values('id', 'approved_comments')
            cache.set(comments_cache_key, comments, timeout=1200)
        # context['comment'] = comments

        comment_dict = {item['id']: item['approved_comments'] for item in comments}

        likes_cache_key = 'post_like'
        likes = cache.get(likes_cache_key)

        if not likes:
            likes = BlogPost.objects.annotate(like_count=Count('likes')).values('id', 'like_count')
            cache.set(likes_cache_key, likes, timeout=1200)
        # context['likes'] = likes

        like_dict = {item['id']: item['like_count'] for item in likes}

        for post in context['obj']:
            post.approved_comments = comment_dict.get(post.id, 0)
            post.like_count = like_dict.get(post.id, 0)

        context['query'] = self.request.GET.get('q', '')

        return context


class DeletePostView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)
        post.delete()
        messages.success(request, 'The post was deleted successfully.')
        return redirect('core:posts')