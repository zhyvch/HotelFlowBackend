from django.contrib import admin
from src.apps.hotel.models import (
    Category, Amenity, Room, RoomImage, RoomAmenity,
    Booking, BookingCustomer, BookingPayment, QRCode, Review
)

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1

class RoomAmenityInline(admin.TabularInline):
    model = RoomAmenity
    extra = 1

class BookingCustomerInline(admin.TabularInline):
    model = BookingCustomer
    extra = 1

class BookingPaymentInline(admin.TabularInline):
    model = BookingPayment
    extra = 0

class QRCodeInline(admin.TabularInline):
    model = QRCode
    extra = 0

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_per_night', 'status', 'category')
    list_filter = ('status', 'category')
    search_fields = ('title',)
    inlines = [RoomImageInline, RoomAmenityInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'check_in', 'check_out', 'total_price', 'status', 'room')
    list_filter = ('status',)
    search_fields = ('id',)
    date_hierarchy = 'check_in'
    inlines = [BookingCustomerInline, BookingPaymentInline]


@admin.register(BookingCustomer)
class BookingCustomerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'booking', 'is_owner')
    list_filter = ('is_owner',)
    inlines = [QRCodeInline, ReviewInline]


@admin.register(BookingPayment)
class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = ('amount', 'status', 'booking', 'created_at')
    list_filter = ('status',)
    date_hierarchy = 'created_at'


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('qr_code', 'status', 'created_at', 'booking_customer')
    list_filter = ('status',)
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('rating', 'content', 'booking_customer', 'created_at')
    list_filter = ('rating',)