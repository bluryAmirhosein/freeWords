from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from core.models import Comment


@receiver([post_save, post_delete], sender=Comment)
def update_comments_and_reply_cache(sender, instance, **kwarg):
    cache.delete('approved_comments_in_admin_profile')
    cache.delete('approved_reply_in_admin_profile')


