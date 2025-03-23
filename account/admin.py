from django.contrib import admin
from .models import CustomUser, ProfileUser
from django.contrib.auth.admin import UserAdmin
from image_cropping.admin import ImageCroppingMixin


class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for the CustomUser model.

    This class customizes the admin panel for managing users, including:
    - Displaying specific fields in the user list
    - Adding search, filtering, and ordering functionalities
    - Customizing the user creation/editing forms
    """
    model = CustomUser

    # Fields to display in the admin user list
    list_display = ['username', 'full_name', 'email', 'is_staff', 'is_active']

    # Filters available in the admin panel
    list_filter = ['is_staff', 'is_active']

    # Fields that can be searched in the admin panel
    search_fields = ['username', 'email']

    # Default ordering of users in the admin list
    ordering = ['username']

    # Field structure for viewing/editing user details
    fieldsets = (
        (None, {'fields': ('username', 'password')}),  # Basic authentication fields
        ('Personal info', {'fields': ('full_name', 'email')}),  # User personal details
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  # User role and permissions
        ('Important dates', {'fields': ('last_login', 'date_joined')}),   # Login and registration timestamps
    )

    # Field structure for creating a new user in the admin panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # Applies styling for a wider form layout
            'fields': ('username', 'password1', 'password2', 'full_name', 'email', 'is_staff')}
         ),
    )

# Registering the custom user model with the admin panel
admin.site.register(CustomUser, CustomUserAdmin)


class ProfileUserAdmin(ImageCroppingMixin, admin.ModelAdmin):
    """
    Admin configuration for the ProfileUser model.

    This class customizes the admin panel for managing user profiles, including:
    - Displaying user and last update time in the list view
    - Enabling search functionality by username
    - Adding filtering options by user
    - Structuring fields for editing user profiles
    """

    # Fields to display in the profile list in the admin panel
    list_display = ('user', 'updated')

    # Fields that can be searched in the admin panel (searching by username)
    search_fields = ('user__username',)

    # Filters available in the admin panel (filtering by user)
    list_filter = ('user',)

    # Field structure for editing profile details
    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'photo',)  # Fields available in the profile form
        }),
    )

# Registering the ProfileUser model with the admin panel
admin.site.register(ProfileUser, ProfileUserAdmin)