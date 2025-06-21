from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import FitnessClass, Booking
from .serializers import (
    FitnessClassSerializer,
    BookingRequestSerializer,
    BookingSerializer,
    BookingResponseSerializer
)
import logging

logger = logging.getLogger('booking')


class ClassListView(APIView): 
    def get(self, request):
        try:
            upcoming_classes = FitnessClass.objects.filter(
                datetime_utc__gt=timezone.now()
            ).order_by('datetime_utc')
            
            serializer = FitnessClassSerializer(upcoming_classes, many=True)
            
            logger.info(f"Retrieved {len(upcoming_classes)} upcoming classes")
            
            return Response({
                'status': 'success',
                'count': len(upcoming_classes),
                'classes': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving classes: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to retrieve classes'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookClassView(APIView):
    def post(self, request):
        try:
            serializer = BookingRequestSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid booking request: {serializer.errors}")
                return Response({
                    'status': 'error',
                    'message': 'Invalid booking data',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            with transaction.atomic():
                fitness_class = FitnessClass.objects.select_for_update().get(
                    id=validated_data['class_id']
                )
                if not fitness_class.is_bookable():
                    return Response({
                        'status': 'error',
                        'message': 'Class is no longer available for booking'
                    }, status=status.HTTP_400_BAD_REQUEST)

                booking = Booking.objects.create(
                    fitness_class=fitness_class,
                    client_name=validated_data['client_name'],
                    client_email=validated_data['client_email'].lower(),
                    status='CONFIRMED'
                )
                
                fitness_class.refresh_from_db()
                
                response_data = {
                    'message': 'Booking confirmed successfully',
                    'booking_id': booking.id,
                    'class_name': fitness_class.name,
                    'class_datetime_ist': fitness_class.get_ist_datetime().strftime('%Y-%m-%d %H:%M:%S IST'),
                    'client_name': booking.client_name,
                    'client_email': booking.client_email,
                    'remaining_slots': fitness_class.available_slots
                }
                
                response_serializer = BookingResponseSerializer(response_data)
                
                logger.info(f"Booking created: ID {booking.id} for {booking.client_email}")
                
                return Response({
                    'status': 'success',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except FitnessClass.DoesNotExist:
            logger.error(f"Fitness class not found: {validated_data.get('class_id')}")
            return Response({
                'status': 'error',
                'message': 'Fitness class not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        except ValidationError as e:
            logger.error(f"Validation error during booking: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Unexpected error during booking: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Booking failed due to server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BookingListView(APIView):
    def get(self, request):
        try:
            client_email = request.query_params.get('email')
            
            if not client_email:
                return Response({
                    'status': 'error',
                    'message': 'Email parameter is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from django.core.validators import EmailValidator
            from django.core.exceptions import ValidationError
            
            email_validator = EmailValidator()
            try:
                email_validator(client_email)
            except ValidationError:
                return Response({
                    'status': 'error',
                    'message': 'Invalid email format'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            bookings = Booking.objects.filter(
                client_email=client_email.lower(),
                status='CONFIRMED'
            ).select_related('fitness_class').order_by('-booking_time')
            
            serializer = BookingSerializer(bookings, many=True)
            
            logger.info(f"Retrieved {len(bookings)} bookings for {client_email}")
            
            return Response({
                'status': 'success',
                'count': len(bookings),
                'email': client_email,
                'bookings': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving bookings: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Failed to retrieve bookings'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

