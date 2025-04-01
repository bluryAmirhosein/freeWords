# core_forms Documentation

## Overview

The `core_forms.py` file contains the **forms** used for user interactions with the **Comment**, **Reply**, and **BlogPost** models. These forms facilitate the submission of **comments**, **replies**, and the creation of **blog posts**. The file uses Django's **ModelForm** to create forms based on the models and includes custom widgets for styling and user-friendly input.

### 📌 **Key Forms**
- **💬 `CommentForm`**: Allows users to submit a comment on a blog post with a styled textarea for content.
- **💬 `ReplyForm`**: Similar to `CommentForm` but used for replying to existing comments.
- **📝 `PostCreationForm`**: Enables admins to create a new blog post by entering title, description, slug, cover image, and tags.

These forms help streamline the process of interacting with the blog system and are integral to the functionality of comments, replies, and post creation.

---

## 📝 **Form Specifications**  
Below is the full reference for the `core.forms`:

::: core.forms
