from django.urls import path, include

urlpatterns = [
    path('users/', include('src.apps.users.urls')),
]