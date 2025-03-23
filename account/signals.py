from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from core.models import Comment


@receiver([post_save, post_delete], sender=Comment)
def update_comments_and_reply_cache(sender, instance, **kwarg):
    """
    Signal receiver that listens to post_save and post_delete signals for the Comment model.
    When a comment or a reply is approved or deleted, it deletes the relevant cache keys:
    'approved_comments_in_admin_profile' and 'approved_reply_in_admin_profile'.
    This ensures that the cache is refreshed with the most up-to-date data for the admin profile.
    """
    # Deleting cache related to approved comments and replies in the admin profile
    cache.delete('approved_comments_in_admin_profile')
    cache.delete('approved_reply_in_admin_profile')


