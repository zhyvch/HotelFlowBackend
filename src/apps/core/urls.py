from django.urls import path, include

urlpatterns = [
    path('v1/', include('src.apps.core.v1.urls')),
]