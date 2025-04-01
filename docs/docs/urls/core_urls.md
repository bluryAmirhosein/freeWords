# Core URLs Documentation

## Overview

The `core_urls.py` file defines the **URL patterns** for managing blog-related views, including displaying blog posts, creating and editing posts, handling comments, and liking posts. These URLs allow users to interact with the blog content on the platform.

### 📌 **Main URLs**
- **🏠 Home (`/`)** → Displays the home page of the site.
- **📄 Blog Post Detail (`/post-detail/<pk>/<slug>/`)** → Displays a detailed view of a specific blog post based on its primary key and slug.
- **🗑️ Delete Comment (`/comment/delete/<comment_id>/`)** → Allows users to delete a comment they have posted.
- **💬 Reply to Comment (`/comment/reply/<post_id>/<comment_id>/`)** → Enables users to reply to a specific comment on a blog post.
- **🗑️ Delete Reply (`/reply/<reply_id>/delete/`)** → Allows users to delete a reply to a comment.
- **👍 Like Post (`/post/<pk>/<slug>/like/`)** → Allows users to like a specific blog post.
- **📝 Post Creation (`/post-creation/`)** → Displays a form for users to create a new blog post.
- **✏️ Post Edit (`/post-creation/<pk>/`)** → Displays a form to edit an existing blog post (based on its primary key).
- **📋 Posts List (`/posts/`)** → Displays a list of all blog posts.
- **🗑️ Delete Post (`/posts/delete/<pk>/`)** → Allows users to delete a specific blog post.

All URLs are mapped to their respective views, handling the necessary functionality like rendering templates, processing form submissions, and performing actions like creating, editing, or deleting content.

---

