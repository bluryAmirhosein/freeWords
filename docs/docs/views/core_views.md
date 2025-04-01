# Core Views Documentation

## Overview

The `core/views.py` file defines the views that handle the logic for displaying and interacting with blog posts, comments, likes, and replies. This module provides the functionality for users to view posts, comment on them, reply to comments, like posts, and manage content. It also includes views for post creation and editing, accessible only to superusers.

### 📌 **Key Views**
- **🏠 `HomeView`** → Displays the homepage with a list of blog posts and top content.
- **📝 `BlogPostDetailView`** → Displays detailed information for a specific blog post, including comments and replies.
- **💬 `ReplyCommentView`** → Handles adding and editing replies to comments.
- **👍 `LikePostView`** → Manages liking and unliking of blog posts.
- **✏️ `PostCreationView`** → Allows superusers to create or edit blog posts.

These views offer a seamless and dynamic user experience, leveraging caching for optimized performance.

---

## 📝 **View Specifications**  
Below is the full reference for the `core.views` file:

::: core.views
