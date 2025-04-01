# core_admin Documentation

## Overview

The `core_admin.py` file contains the admin configurations for managing various core models such as **BlogPost**, **Comment**, **Tag**, and **PostLike** within the Django admin panel. These configurations are customized to enhance the user experience for managing blog content, comments, tags, and post likes.

### 📌 **Key Admin Classes**

- **📝 `BlogPostAdmin`**: Admin configuration for managing **BlogPost** models, including:
  - Displaying the title, creation date, and cover image in the admin list view.
  - Enabling filtering by creation date.
  - Adding search functionality by title and description.
  - Automatically generating slugs based on the title.

- **💬 `CommentAdmin`**: Admin configuration for managing **Comment** models, including:
  - Displaying post title, user, and creation date.
  - Enabling search by post title, username, and content.

- **🏷️ `TagAdmin`**: Admin configuration for managing **Tag** models, including:
  - Displaying tag name and creation date.
  - Enabling filtering by tag name.

- **❤️ `PostLikeAdmin`**: Admin configuration for managing **PostLike** models, including:
  - Displaying user and post information.
  - Enabling filtering by post.

---

## 📝 **Admin Specifications**  
Below is the full reference for the `core.admin`:

::: core.admin
