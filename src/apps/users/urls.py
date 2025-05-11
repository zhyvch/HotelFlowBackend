from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from src.apps.users.views import UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='')

token_auth_urls = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    path('auth/', include(token_auth_urls)),
] + router.urls
