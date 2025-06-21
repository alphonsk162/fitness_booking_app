from django.db import models
from django.core.validators import EmailValidator, MinValueValidator
from django.utils import timezone
import pytz


class FitnessClass(models.Model):
  
    CLASS_TYPES = [
        ('YOGA', 'Yoga'),
        ('ZUMBA', 'Zumba'),
        ('HIIT', 'HIIT'),
    ]
    
    name = models.CharField(
        max_length=20, 
        choices=CLASS_TYPES,
    )
    datetime_utc = models.DateTimeField()
    instructor = models.CharField(
        max_length=100
    )
    total_slots = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    available_slots = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['datetime_utc']
    
    def get_ist_datetime(self):
        ist = pytz.timezone('Asia/Kolkata')
        return self.datetime_utc.astimezone(ist)
    
    def is_bookable(self):
        return self.available_slots > 0 and self.datetime_utc > timezone.now()
    
    def save(self, *args, **kwargs):
        if self.available_slots > self.total_slots:
            self.available_slots = self.total_slots
        super().save(*args, **kwargs)


class Booking(models.Model): 
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    fitness_class = models.ForeignKey(
        FitnessClass,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    client_name = models.CharField(
        max_length=100,
    )
    client_email = models.EmailField(
        validators=[EmailValidator()],
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='CONFIRMED',
    )
    booking_time = models.DateTimeField(
        auto_now_add=True,
    )
    
    class Meta:
        ordering = ['-booking_time']
        unique_together = ['fitness_class', 'client_email']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
    
    def __str__(self):
        return f"{self.client_name} - {self.fitness_class.name} - {self.status}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if is_new and self.status == 'CONFIRMED':
            if self.fitness_class.available_slots > 0:
                self.fitness_class.available_slots -= 1
                self.fitness_class.save()
            else:
                raise ValueError("No available slots for this class")
        
        super().save(*args, **kwargs)