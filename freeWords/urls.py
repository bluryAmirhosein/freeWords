"""
URL configuration for freeWords project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from ckeditor_uploader import urls as ckeditor_urls


# URL configurations for the project
urlpatterns = [
    # Admin panel URL, accessible at '/admin/'.
    # This includes the default Django admin site for managing the application.
    path('admin/', admin.site.urls),

    # Including URLs from the 'core' app, making the paths of 'core' available under the base URL ('').
    # The namespace 'core' is used to reverse the URLs with the specified namespace in templates and views.
    path('', include('core.urls', namespace='core')),

    # Including URLs from the 'account' app, which handles user authentication and account-related views.
    # The namespace 'account' is used for URL reversal within the 'account' app.
    path('account/', include('account.urls', namespace='account')),

    # Including URLs for CKEditor, a rich text editor used in forms. These are necessary for CKEditor functionality.
    path('cheditor/', include(ckeditor_urls)),
]

# If in DEBUG mode, serve media files (images, documents, etc.) directly.
# This is useful in development, but not for production.
# The MEDIA_URL and MEDIA_ROOT settings are used to determine where the media files are stored and accessed.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)