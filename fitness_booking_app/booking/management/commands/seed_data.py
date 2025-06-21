from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
import random
from booking.models import FitnessClass, Booking


class Command(BaseCommand):
    help = 'Seed the database with sample fitness classes and bookings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--classes',
            type=int,
            default=10,
            help='Number of fitness classes to create'
        )
        parser.add_argument(
            '--bookings',
            type=int,
            default=5,
            help='Number of sample bookings to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Booking.objects.all().delete()
            FitnessClass.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        self.stdout.write('Creating fitness classes...')
        classes_created = self.create_fitness_classes(options['classes'])
        
        self.stdout.write('Creating sample bookings...')
        bookings_created = self.create_sample_bookings(options['bookings'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {classes_created} classes and {bookings_created} bookings'
            )
        )

    def create_fitness_classes(self, count):
        """Create sample fitness classes with varied schedules"""
        
        instructors = {
            'YOGA': ['Priya Sharma', 'Anjali Gupta', 'Rajesh Kumar'],
            'ZUMBA': ['Maria Rodriguez', 'Carlos Silva', 'Isabella Santos'],
            'HIIT': ['John Thompson', 'Sarah Wilson', 'Mike Johnson']
        }
        
        ist = pytz.timezone('Asia/Kolkata')
        utc = pytz.UTC
        
        classes_created = 0

        for day_offset in range(7):
            base_date = timezone.now().date() + timedelta(days=day_offset)
            
            for _ in range(random.randint(2, 3)):
                class_type = random.choice(['YOGA', 'ZUMBA', 'HIIT'])
                instructor = random.choice(instructors[class_type])

                hour = random.choice([6, 7, 8, 9, 10, 16, 17, 18, 19, 20])
                minute = random.choice([0, 30])

                ist_datetime = ist.localize(
                    datetime.combine(base_date, datetime.min.time().replace(hour=hour, minute=minute))
                )
                utc_datetime = ist_datetime.astimezone(utc)

                total_slots = random.randint(10, 20)
                available_slots = random.randint(5, total_slots)
                
                FitnessClass.objects.create(
                    name=class_type,
                    datetime_utc=utc_datetime,
                    instructor=instructor,
                    total_slots=total_slots,
                    available_slots=available_slots
                )
                
                classes_created += 1
                
                if classes_created >= count:
                    return classes_created
        
        return classes_created

    def create_sample_bookings(self, count):
        """Create sample bookings for testing"""
        
        sample_clients = [
            ('Rahul Patel', 'rahul.patel@email.com'),
            ('Sneha Reddy', 'sneha.reddy@email.com'),
            ('Arjun Singh', 'arjun.singh@email.com'),
            ('Kavya Nair', 'kavya.nair@email.com'),
            ('Vikram Joshi', 'vikram.joshi@email.com'),
            ('Pooja Agarwal', 'pooja.agarwal@email.com'),
            ('Rohan Gupta', 'rohan.gupta@email.com'),
            ('Divya Sharma', 'divya.sharma@email.com'),
        ]

        available_classes = FitnessClass.objects.filter(
            datetime_utc__gt=timezone.now(),
            available_slots__gt=0
        )
        
        if not available_classes.exists():
            self.stdout.write(self.style.WARNING('No available classes found for booking'))
            return 0
        
        bookings_created = 0
        
        for _ in range(count):
            if bookings_created >= len(sample_clients):
                break
                
            client_name, client_email = sample_clients[bookings_created]
            fitness_class = random.choice(available_classes)
            
            try:
                if not Booking.objects.filter(
                    fitness_class=fitness_class,
                    client_email=client_email
                ).exists():
                    
                    Booking.objects.create(
                        fitness_class=fitness_class,
                        client_name=client_name,
                        client_email=client_email,
                        status='CONFIRMED'
                    )
                    bookings_created += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Failed to create booking: {str(e)}')
                )
        
        return bookings_created