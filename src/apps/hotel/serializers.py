from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction
from src.apps.hotel.models import Booking, Room, BookingCustomer, Category, Amenity, QRCode


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
        ]
        extra_kwargs = {
            'description': {'required': False},
        }


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = [
            'id',
            'name',
            'icon',
            'description',
        ]
        extra_kwargs = {
            'description': {'required': False},
        }


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id',
            'title',
            'description',
            'price_per_night',
            'status',
            'category',
            'amenities',
        ]
        depth = 1
        extra_kwargs = {
            'status': {'read_only': True},
            'amenities': {'required': False},
        }


class BookingCustomerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    is_owner = serializers.BooleanField()
    email = serializers.EmailField(source='customer.email')
    phone_number = serializers.CharField(source='customer.phone_number')
    first_name = serializers.CharField(source='customer.first_name')
    last_name = serializers.CharField(source='customer.last_name')


    class Meta:
        model = BookingCustomer
        fields = [
            'id',
            'is_owner',
            'email',
            'phone_number',
            'first_name',
            'last_name',
        ]


class BookingSerializer(serializers.ModelSerializer):
    customers = BookingCustomerSerializer(source='booking_customers', many=True, read_only=True)
    additional_customer_ids = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), many=True, write_only=True, required=False)
    room_id = serializers.PrimaryKeyRelatedField(source='room', queryset=Room.objects.all(), write_only=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'check_in',
            'check_out',
            'total_price',
            'status',
            'room',
            'customers',
            'additional_customer_ids',
            'room_id',
        ]
        depth = 1
        extra_kwargs = {
            'total_price': {'read_only': True},
            'status': {'read_only': True},
        }

    @transaction.atomic
    def create(self, validated_data):
        additional_customers = validated_data.pop('additional_customer_ids', [])
        room = validated_data.get('room')
        check_in = validated_data.get('check_in')
        check_out = validated_data.get('check_out')

        days = (check_out - check_in).days
        total_price = (room.price_per_night * days) + 100

        validated_data['total_price'] = total_price

        booking = Booking.objects.create(**validated_data)

        if self.context['request'].user:
            BookingCustomer.objects.create(
                booking=booking,
                customer=self.context['request'].user,
                is_owner=True
            )

        for customer in additional_customers:
            BookingCustomer.objects.create(
                booking=booking,
                customer=customer,
                is_owner=False
            )

        return booking

    @transaction.atomic
    def update(self, instance, validated_data):
        additional_customers = validated_data.pop('additional_customer_ids', None)

        recalculate = False
        if 'check_in' in validated_data or 'check_out' in validated_data or 'room' in validated_data:
            recalculate = True

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if recalculate:
            days = (instance.check_out - instance.check_in).days
            instance.total_price = (instance.room.price_per_night * days) + 100

        instance.save()

        if additional_customers is not None:
            owner_relationship = instance.booking_customers.filter(is_owner=True).first()

            instance.booking_customers.filter(is_owner=False).delete()

            for customer in additional_customers:
                BookingCustomer.objects.create(
                    booking=instance,
                    customer=customer,
                    is_owner=False
                )

        return instance

class QRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRCode
        fields = '__all__'
        depth = 1
