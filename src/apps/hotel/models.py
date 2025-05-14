from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.apps.common.models import TitledTimestampedBaseModel, TimestampedBaseModel


class Category(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
        null=False,
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Amenity(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=50,
        null=False,
    )
    icon = models.ImageField(
        verbose_name=_('Icon'),
        upload_to='amenities/',
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Amenity')
        verbose_name_plural = _('Amenities')


class Room(TitledTimestampedBaseModel):
    class RoomStatus(models.TextChoices):
        FREE = 'free', _('Free')
        BUSY = 'busy', _('Busy')
        OPERATED = 'operated', _('Operated')

    description = models.TextField(
        verbose_name=_('Description'),
        null=True,
    )
    price_per_night = models.DecimalField(
        verbose_name=_('Price per night'),
        max_digits=10,
        decimal_places=2,
        null=False,
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=RoomStatus,
        default=RoomStatus.FREE,
        null=False,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name=_('Category'),
    )
    amenities = models.ManyToManyField(
        Amenity,
        through='RoomAmenity',
        related_name='rooms',
        verbose_name=_('Amenities'),
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')


class RoomImage(models.Model):
    image = models.ImageField(
        verbose_name=_('Image'),
        upload_to='room_images/',
        null=False,
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Room'),
    )

    def __str__(self):
        return f'Image {self.image.name} for {self.room.title}'

    class Meta:
        verbose_name = _('Room Image')
        verbose_name_plural = _('Room Images')


class RoomAmenity(models.Model):
    amenity = models.ForeignKey(
        Amenity,
        on_delete=models.CASCADE,
        related_name='room_amenities',
        verbose_name=_('Amenity'),
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='room_amenities',
        verbose_name=_('Room'),
    )

    def __str__(self):
        return f'{self.room.title} - {self.amenity.name}'

    class Meta:
        verbose_name = _('Room Amenity')
        verbose_name_plural = _('Room Amenities')
        constraints = [
            models.UniqueConstraint(
                fields=['amenity', 'room'],
                name='unique_room_amenity',
            )
        ]


class Booking(TimestampedBaseModel):
    class BookingStatus(models.TextChoices):
        CREATED = 'created', _('Created')
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        CANCELED = 'canceled', _('Canceled')

    check_in = models.DateTimeField(
        verbose_name=_('Check-in'),
        null=False,
    )
    check_out = models.DateTimeField(
        verbose_name=_('Check-out'),
        null=False,
    )
    total_price = models.DecimalField(
        verbose_name=_('Total price'),
        max_digits=10,
        decimal_places=2,
        null=False,
    )
    status = models.CharField(
        verbose_name=_('Booking status'),
        max_length=20,
        choices=BookingStatus,
        default=BookingStatus.CREATED,
        null=False,
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('Room'),
    )
    customers = models.ManyToManyField(
        get_user_model(),
        through='BookingCustomer',
        related_name='bookings',
        verbose_name=_('Customers'),
    )

    def __str__(self):
        return f'Booking for {self.room.title} from {self.check_in} to {self.check_out}'

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_in__lt=models.F('check_out')),
                name='check_in_before_check_out',
            ),
            models.UniqueConstraint(
                fields=['room', 'check_in', 'check_out'],
                name='unique_booking_room_dates',
            )
        ]


class BookingCustomer(models.Model):
    customer = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='booking_customers',
        verbose_name=_('Customer'),
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='booking_customers',
        verbose_name=_('Booking'),
    )
    is_owner = models.BooleanField(
        verbose_name=_('Is owner'),
        default=False,
    )

    def __str__(self):
        return f'{self.customer.email} - {self.booking.room.title}'

    class Meta:
        verbose_name = _('Booking Customer')
        verbose_name_plural = _('Booking Customers')
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'booking'],
                name='unique_booking_customer',
            )
        ]


class BookingPayment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        COMPLETED = 'completed', _('Completed')
        CANCELED = 'canceled', _('Canceled')

    amount = models.DecimalField(
        verbose_name=_('Amount'),
        max_digits=10,
        decimal_places=2,
        null=False,
    )
    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
        null=False,
    )
    status = models.CharField(
        verbose_name=_('Payment status'),
        max_length=20,
        choices=PaymentStatus,
        default=PaymentStatus.PENDING,
        null=False,
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Booking'),
    )

    def __str__(self):
        return f'Payment for {self.booking.room.title} - {self.amount}'

    class Meta:
        verbose_name = _('Booking Payment')
        verbose_name_plural = _('Booking Payments')


class QRCode(models.Model):
    class QRStatus(models.TextChoices):
        BLACKLISTED = 'blacklisted', _('Blacklisted')
        ACTIVE = 'active', _('Active')

    qr_code = models.ImageField(
        verbose_name=_('QR Code'),
        upload_to='qr_codes/',
        null=False,
    )
    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
        null=False,
    )
    booking_customer = models.ForeignKey(
        BookingCustomer,
        on_delete=models.CASCADE,
        related_name='qr_codes',
        verbose_name=_('Booking customer'),
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=QRStatus,
        default=QRStatus.ACTIVE,
        null=False,
    )

    def __str__(self):
        return f'QR Code for {self.booking_customer.customer.email} - {self.qr_code}'

    class Meta:
        verbose_name = _('QR Code')
        verbose_name_plural = _('QR Codes')


class Review(TitledTimestampedBaseModel):
    rating = models.PositiveIntegerField(
        verbose_name=_('Rating'),
        default=5,
        null=False,
    )
    content = models.TextField(
        verbose_name=_('Content'),
        null=True,
    )
    booking_customer = models.OneToOneField(
        BookingCustomer,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name=_('Booking customer'),
    )

    def __str__(self):
        return f'Review by {self.booking_customer.customer.email} - {self.title}'

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

