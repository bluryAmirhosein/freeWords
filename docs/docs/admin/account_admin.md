# account_admin Documentation

## Overview

The `account_admin.py` file contains **admin configurations** for managing the **CustomUser** and **ProfileUser** models in the Django admin panel. This file extends the default admin functionalities to provide a more customized experience for managing user accounts and profiles.

### 📌 **Key Admin Classes**
- **👤 `CustomUserAdmin`**: A custom configuration for the **CustomUser** model, allowing:
  - Custom display of user information (username, full name, email, etc.).
  - Filtering, search, and ordering options for easier management.
  - Enhanced user creation and editing forms.
  
- **🖼️ `ProfileUserAdmin`**: A custom admin for managing **ProfileUser** information, including:
  - Displaying the associated user and the last update time.
  - Enabling search by username and filtering by user.
  - Organizing the fields for editing user profile details (e.g., bio, photo).

These configurations allow administrators to efficiently manage user accounts and profiles with added customization and user-friendly features.

---

## 📝 **Admin Specifications**  
Below is the full reference for the `account.admin`:

::: account.admin
