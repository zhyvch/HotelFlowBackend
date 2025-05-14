import json
import io

import qrcode
from django.utils import timezone
from django.core.files.base import ContentFile
from qrcode.main import QRCode as QRCodeFactory
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from src.apps.hotel.models import Booking, Room, QRCode, Category, Amenity
from src.apps.hotel.serializers import QRCodeSerializer, BookingSerializer, RoomSerializer, CategorySerializer, AmenitySerializer


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AmenityViewSet(ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer


class RoomViewSet(ReadOnlyModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        booking = self.get_object()
        booking_customers = booking.booking_customers
        if booking.status != Booking.BookingStatus.CREATED:
            raise ValidationError('Booking already activated.')

        if booking.check_in > timezone.now():
            raise ValidationError('Cannot activate a booking before check-in.')

        if request.user not in booking.customers.all():
            raise ValidationError('You are not authorized to activate this booking.')

        booking.status = Booking.BookingStatus.ACTIVE
        booking.save()

        qr_codes = []
        for booking_customer in booking_customers.all():
            data = json.dumps({
                'user_id': booking_customer.customer.id,
                'booking_id': booking_customer.booking.id
            })

            qr = QRCodeFactory(
                version=3,
                box_size=10,
                border=5,
                error_correction=qrcode.constants.ERROR_CORRECT_H
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color='black', back_color='white')

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            qr_code = QRCode(booking_customer=booking_customer)
            qr_code.qr_code.save(
                f'qr_code_{booking_customer.id}.png',
                ContentFile(buffer.getvalue()),
                save=False
            )
            qr_codes.append(qr_code)

        QRCode.objects.bulk_create(qr_codes)
        return Response(status=201)

    @action(detail=True)
    def qr_code(self, request, pk=None):
        booking = self.get_object()

        if request.user not in booking.customers.all():
            raise ValidationError('You are not authorized to activate this booking.')

        if booking.status != Booking.BookingStatus.ACTIVE:
            raise ValidationError('Booking already activated.')

        try:
            qr = QRCode.objects.get(
                booking_customer__customer=request.user,
                booking_customer__booking=booking,
                status=QRCode.QRStatus.ACTIVE
            )
        except QRCode.DoesNotExist:
            raise ValidationError('QR code not found.')

        serializer = QRCodeSerializer(qr)

        return Response(serializer.data, status=200)

