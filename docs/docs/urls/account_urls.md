# Account URLs Documentation

## Overview

The `account_urls.py` file defines the **URL patterns** for handling user authentication, registration, password management, and profile viewing. These URLs are essential for managing user sessions and profiles within the platform.

### 📌 **Main URLs**
- **🔑 Sign Up (`/signup/`)** → Allows users to register an account on the platform.
- **🔓 Log In (`/login/`)** → Enables users to log into their account.
- **🚪 Log Out (`/logout/`)** → Logs out the currently authenticated user from their account.
- **🔑 Forget Password (`/forget-pass/`)** → Provides a way for users to reset their password if forgotten.
- **🔑 Reset Password (`/reset-password/<uidb64>/<token>/`)** → Allows users to reset their password using a token.
- **👤 User Profile (`/userprofile/<user_id>/`)** → Displays a specific user’s profile.
- **💬 Comment Management (`/comment/action/<comment_id>/`)** → Admins can manage (approve or delete) user comments.

All URLs correspond to views that are responsible for rendering the necessary templates and handling form submissions or actions.

---


