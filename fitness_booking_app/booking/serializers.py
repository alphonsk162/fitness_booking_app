from rest_framework import serializers
from django.utils import timezone
from .models import FitnessClass, Booking
import pytz


class FitnessClassSerializer(serializers.ModelSerializer):
    datetime_ist = serializers.SerializerMethodField()
    is_bookable = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessClass
        fields = [
            'id',
            'name',
            'datetime_utc',
            'datetime_ist',
            'instructor',
            'total_slots',
            'available_slots',
            'is_bookable'
        ]
        read_only_fields = ['id', 'datetime_ist', 'is_bookable']
    
    def get_datetime_ist(self, obj):
        ist_time = obj.get_ist_datetime()
        return ist_time.strftime('%Y-%m-%d %H:%M:%S IST')
    
    def get_is_bookable(self, obj):
        return obj.is_bookable()


class BookingRequestSerializer(serializers.Serializer):
    class_id = serializers.IntegerField(min_value=1)
    client_name = serializers.CharField(
        max_length=100,
        min_length=2,
        allow_blank=False,
        trim_whitespace=True
    )
    client_email = serializers.EmailField()
    
    def validate_class_id(self, value):
        try:
            fitness_class = FitnessClass.objects.get(id=value)
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Fitness class not found.")
        
        if not fitness_class.is_bookable():
            if fitness_class.available_slots <= 0:
                raise serializers.ValidationError("No available slots for this class.")
            elif fitness_class.datetime_utc <= timezone.now():
                raise serializers.ValidationError("Cannot book past classes.")
        
        return value
    
    def validate_client_name(self, value):
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError("Name should only contain letters and spaces.")
        return value.title()  
    
    def validate(self, data):
        fitness_class = FitnessClass.objects.get(id=data['class_id'])
        client_email = data['client_email'].lower()
        existing_booking = Booking.objects.filter(
            fitness_class=fitness_class,
            client_email=client_email,
            status='CONFIRMED'
        ).exists()
        
        if existing_booking:
            raise serializers.ValidationError({
                'client_email': 'You have already booked this class.'
            })
        
        return data


class BookingSerializer(serializers.ModelSerializer):

    class_name = serializers.CharField(source='fitness_class.name', read_only=True)
    class_datetime_ist = serializers.SerializerMethodField()
    instructor = serializers.CharField(source='fitness_class.instructor', read_only=True)
    booking_time_ist = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id',
            'class_name',
            'class_datetime_ist',
            'instructor',
            'client_name',
            'client_email',
            'status',
            'booking_time',
            'booking_time_ist'
        ]
        read_only_fields = ['id', 'booking_time', 'booking_time_ist']
    
    def get_class_datetime_ist(self, obj):
        ist_time = obj.fitness_class.get_ist_datetime()
        return ist_time.strftime('%Y-%m-%d %H:%M:%S IST')
    
    def get_booking_time_ist(self, obj):
        ist = pytz.timezone('Asia/Kolkata')
        ist_time = obj.booking_time.astimezone(ist)
        return ist_time.strftime('%Y-%m-%d %H:%M:%S IST')


class BookingResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    booking_id = serializers.IntegerField()
    class_name = serializers.CharField()
    class_datetime_ist = serializers.CharField()
    client_name = serializers.CharField()
    client_email = serializers.EmailField()
    remaining_slots = serializers.IntegerField()