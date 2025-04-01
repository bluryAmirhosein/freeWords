# account_forms Documentation

## Overview

The `account_forms.py` file contains several **forms** used for managing user account-related activities, such as **sign-up**, **password reset**, and **user profile updates**. These forms utilize Django’s **ModelForm** to manage form validation and data handling for user-related models.

### 📌 **Key Forms**
- **📝 `SignUpForm`**: A form for **user registration**, which includes validation for unique usernames and emails, as well as password confirmation.
- **🔑 `ForgetPasswordForm`**: A simple form where users can enter their registered email to initiate a **password reset** process.
- **🔒 `ResetPasswordForm`**: A form to allow users to reset their password, ensuring the **new password matches** the confirmation.
- **👤 `CustomUserForm`**: A form used for **updating a user's full name**.
- **🖼️ `UserProfileForm`**: A form for **updating user profile information**, including **profile photo** and **bio**.

These forms ensure smooth user management and provide an organized way to handle common account operations, from registration to profile updates.

---

## 📝 **Form Specifications**  
Below is the full reference for the `account.forms`:

::: account.forms
