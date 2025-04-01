# Core Signals Documentation

## Overview

The `core_signals.py` file defines several **Django signals** that listen for changes related to **comments**, **profiles**, and **likes**. These signals trigger cache updates or deletions whenever a comment, profile, or like is created, updated, or deleted. This ensures that the data remains fresh and consistent in the cache, improving the performance of the application.

### 📌 **Main Signal Handlers**
- **📝 update_comment_cache_on_change** → Updates the cache for the count of approved comments when a comment is saved or deleted.
- **👤 update_profile_cache_on_change** → Updates the cache for a user's profile when it is created or deleted.
- **👍 update_likes_cache** → Updates the cache related to the like status of a post when a like is added or removed.
- **🗨️ update_comments_cache** → Ensures that the cache for approved comments is up-to-date whenever a comment is saved or deleted.
- **💬 update_user_liked_post_cache** → Refreshes the cache for a user's like status on a specific post.

---

## 📖 **Signal Specifications**
Below is the full implementation of each signal handler:

::: core.signals