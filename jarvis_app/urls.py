from django.urls import path
from . import views

urlpatterns = [
    path('', views.jarvis, name='jarvis'),  # The root URL maps to the `jarvis` view
    path('search/', views.search, name='search'),  # The search URL
]
