# from Tools.demo.mcast import sender
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Comment, BlogPost, PostLike
from account.models import ProfileUser
from django.db.models import Count, Q



def update_comments_cache():
    """
    Updates the cache with the count of approved comments for each blog post.
    The cache key is 'approved_comments_per_post' and stores the blog post IDs
    along with the count of approved comments.
    The cache is set to expire after 20 minutes (1200 seconds).
    """
    comments_cache_key = 'approved_comments_per_post'
    comments = BlogPost.objects.annotate(
        approved_comments=Count('comments', filter=Q(comments__is_approved=True))
    ).values('id', 'approved_comments')
    # Setting the cache with the list of approved comments counts per post
    cache.set(comments_cache_key, comments, timeout=1200)


def update_profile_cache(user_id):
    """
    Updates the cache for a user's profile. If the profile exists, it is cached with the key
    'profile_{user_id}'. If no profile exists for the user, it caches a None value.
    The cache is set to expire after 12 hours (43200 seconds).
    """
    profile_cache_key = f'profile_{user_id}'
    try:
        # Trying to get the profile of the given user ID
        profile = ProfileUser.objects.get(user=user_id)
    except ProfileUser.DoesNotExist:
        profile = None
    # Setting the cache with the user's profile or None if no profile exists
    cache.set(profile_cache_key, profile, timeout=43200)


@receiver([post_save, post_delete], sender=Comment)
def update_comment_cache_on_change(sender, instance, **kwargs):
    """
    Signal receiver that listens to post_save and post_delete signals for Comment model.
    When a comment is saved or deleted, it deletes the cache for approved comments per post
    to ensure the cache is updated with the most recent data.
    """
    # Deleting the cache key for approved comments to trigger a cache refresh on the next update
    cache.delete('approved_comments_per_post')


@receiver([post_save, post_delete], sender=ProfileUser)
def update_profile_cache_on_change(sender, instance, **kwargs):
    """
    Signal receiver that listens to post_save and post_delete signals for ProfileUser model.
    When a profile is saved or deleted, it deletes the user's profile cache to trigger a refresh
    with the most recent data.
    """
    # Deleting the cache for the user's profile to trigger a cache refresh on the next update
    cache.delete(f"profile_{instance.user.id}")


@receiver([post_save, post_delete], sender=PostLike)
def update_likes_cache(sender, instance, **kwargs):
    """
    Signal receiver that listens to post_save and post_delete signals for the PostLike model.
    When a like is added or removed, it deletes the 'post_like' cache key to ensure the cache is updated.
    This ensures that the like count for the post is always up to date.
    """
    # Deleting the cache key 'post_like' to force a cache refresh with the updated like count
    cache_key = 'post_like'
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Comment)
def update_comments_cache(sender, instance, **kwargs):
    """
    Signal receiver that listens to post_save and post_delete signals for the Comment model.
    When a comment is added or removed, it deletes the 'approved_comments' cache key to ensure the cache is updated.
    This ensures that the approved comments count for the post is always up to date.
    """
    # Deleting the cache key 'approved_comments' to force a cache refresh with the updated approved comments count
    cache_key = 'approved_comments'
    cache.delete(cache_key)

@receiver([post_save, post_delete], sender=PostLike)
def update_user_liked_post_cache(sender, instance, **kwargs):
    """
    Signal receiver that listens to post_save and post_delete signals for the PostLike model.
    When a like is added or removed by a user, it deletes the user's cache for that post's like status.
    This ensures that the cache is refreshed the next time the like status for the user is checked.
    """
    # Constructing a cache key that identifies the like status for a specific user and post
    cache_key = f'user_like_{instance.user.id}_liked_post_{instance.post_id}'
    cache.delete(cache_key)
