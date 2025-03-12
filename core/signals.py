from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Comment, BlogPost, PostLike
from account.models import ProfileUser
from django.db.models import Count, Q


def update_comments_cache():
    comments_cache_key = 'approved_comments_per_post'
    comments = BlogPost.objects.annotate(
        approved_comments=Count('comments', filter=Q(comments__is_approved=True))
    ).values('id', 'approved_comments')
    cache.set(comments_cache_key, comments, timeout=1200)


def update_profile_cache(user_id):
    profile_cache_key = f'profile_{user_id}'
    try:
        profile = ProfileUser.objects.get(user=user_id)
    except ProfileUser.DoesNotExist:
        profile = None
    cache.set(profile_cache_key, profile, timeout=43200)


@receiver([post_save, post_delete], sender=Comment)
def update_comment_cache_on_change(sender, instance, **kwargs):
    cache.delete('approved_comments_per_post')


@receiver([post_save, post_delete], sender=ProfileUser)
def update_profile_cache_on_change(sender, instance, **kwargs):
    cache.delete(f"profile_{instance.user.id}")


@receiver([post_save, post_delete], sender=PostLike)
def update_likes_cache(sender, instance, **kwargs):
    cache_key = 'post_like'
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Comment)
def update_comments_cache(sender, instance, **kwargs):
    cache_key = 'approved_comments'
    cache.delete(cache_key)