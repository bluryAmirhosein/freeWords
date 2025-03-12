from django.contrib import admin
from .models import CustomUser, ProfileUser
from django.contrib.auth.admin import UserAdmin
from image_cropping.admin import ImageCroppingMixin


class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ['username', 'full_name', 'email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('full_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'full_name', 'email', 'is_staff')}
         ),
    )


admin.site.register(CustomUser, CustomUserAdmin)


class ProfileUserAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ('user', 'updated')
    search_fields = ('user__username',)
    list_filter = ('user',)

    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'photo',)
        }),
    )


admin.site.register(ProfileUser, ProfileUserAdmin)