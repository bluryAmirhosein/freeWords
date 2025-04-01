# Core Models Documentation

## Overview

The `core_models.py` file defines the **main data models** for managing the blog system, including blog posts, comments, tags, and likes. These models form the backbone of content management and user interaction.

### 📌 **Main Models**
- **🏷️ Tag (`Tag`)** → Categorizes blog posts using unique labels.
- **📝 Blog Post (`BlogPost`)** → Stores blog posts with titles, descriptions, cover images, and associated tags.
- **💬 Comment (`Comment`)** → Handles user comments and replies on blog posts.
- **👍 Post Like (`PostLike`)** → Tracks likes from users on blog posts.

All models follow Django’s **ORM principles** and include utility methods for efficient data retrieval and manipulation.

---

## 📖 **Model Specifications**
Below is the full API reference for the `core.models` module:

::: core.models
