from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.hotel.views import RoomViewSet, CategoryViewSet, AmenityViewSet, BookingViewSet
from apps.users.views import UserViewSet

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='user')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'amenities', AmenityViewSet, basename='amenity')
router.register(r'bookings', BookingViewSet, basename='booking')


auth_urls = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    path('auth/', include(auth_urls)),
] + router.urls
