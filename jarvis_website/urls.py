from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jarvis_app.urls')),  # This includes the URLs from your app
]
