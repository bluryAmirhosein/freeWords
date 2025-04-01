# Account Models Documentation

## Overview

The `account_models.py` file defines the **user authentication** and **profile management** models for the system. This module extends **Django’s built-in authentication system** to add additional user-related information and customizable profile features.

### 📌 **Main Models**
- **👤 `CustomUser`** → Extends Django's default user model, adding fields for **full name**, **email**, and **username**.
- **🖼️ `ProfileUser`** → Stores additional user profile information, such as a **profile photo** and **bio**.

These models allow for enhanced user management and provide utility methods for handling image optimization.

---

## 📝 **Model Specifications**  
Below is the full reference for the `account.models` module:

::: account.models
