# Fitness Studio Booking API

A Django REST API for managing fitness class bookings with proper timezone handling, slot management, and comprehensive error handling.

## Project Structure

```
├── fitness_booking_app
│   ├── booking
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── management
│   │   ├── migrations
│   │   ├── models.py
│   │   ├── __pycache__
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── db.sqlite3
│   ├── fitness_booking_app
│   │   ├── asgi.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── logs
│   │   └── booking.log
│   └── manage.py
├── README.md
└── venv
```

## Features

- **Complete REST API** with 3 main endpoints
- **Timezone Management**: Stores all times in UTC, displays in IST
- **Slot Management**: Real-time tracking of available slots
- **Error Handling**: Comprehensive validation and error responses
- **Database Transactions**: Prevents race conditions during booking
- **Logging**: Detailed logging for monitoring and debugging
- **Sample Data**: Management command to seed test data

## Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/alphonsk162/fitness_booking_app.git
cd fitness_booking_app
```

### 2. Create a Virtual Environment
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```
python manage.py makemigrations
python manage.py migrate
```


### 5. Seed Sample Data

```bash
# Seed with default data (10 classes, 5 bookings)
python manage.py seed_data

# Or customize
python manage.py seed_data --classes 15 --bookings 10

# Clear existing data and reseed
python manage.py seed_data --clear --classes 20
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### 1. GET /api/classes/
Get all upcoming fitness classes.

**Response:**
```json
{
    "status": "success",
    "count": 5,
    "classes": [
        {
            "id": 1,
            "name": "YOGA",
            "datetime_utc": "2025-06-22T04:30:00Z",
            "datetime_ist": "2025-06-22 10:00:00 IST",
            "instructor": "Rahul Patel",
            "total_slots": 15,
            "available_slots": 12,
            "is_bookable": true
        }
    ]
}
```

### 2. POST /api/book/
Book a fitness class.

**Request:**
```json
{
    "class_id": 1,
    "client_name": "Rahul Patel",
    "client_email": "rahul.patel@email.com"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "message": "Booking confirmed successfully",
        "booking_id": 1,
        "class_name": "YOGA",
        "class_datetime_ist": "2025-06-22 10:00:00 IST",
        "client_name": "Rahul Patel",
        "client_email": "rahul.patel@email.com",
        "remaining_slots": 11
    }
}
```

### 3. GET /api/bookings/?email=client@email.com
Get all bookings for a specific email.

**Response:**
```json
{
    "status": "success",
    "count": 2,
    "email": "sneha.reddy@email.com",
    "bookings": [
        {
            "id": 1,
            "class_name": "YOGA",
            "class_datetime_ist": "2025-06-22 10:00:00 IST",
            "instructor": "Priya Sharma",
            "client_name": "Sneha Reddy",
            "client_email": "sneha.reddy@email.com",
            "status": "CONFIRMED",
            "booking_time": "2025-06-21T10:30:00Z",
            "booking_time_ist": "2025-06-21 16:00:00 IST"
        }
    ]
}
```


## Sample cURL Commands

### Get Classes
```bash
curl -X GET http://localhost:8000/api/classes/ \
  -H "Content-Type: application/json"
```

### Book a Class
```bash
curl -X POST http://localhost:8000/api/book/ \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 1,
    "client_name": "Sneha Reddy",
    "client_email": "sneha.reddy@email.com"
  }'
```

### Get Bookings
```bash
curl -X GET "http://localhost:8000/api/bookings/?email=john.doe@email.com" \
  -H "Content-Type: application/json"
```

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input data, validation errors
- **404 Not Found**: Class not found
- **500 Internal Server Error**: Server-side errors

All errors include descriptive messages and maintain consistent JSON structure.

## Timezone Management

- **Storage**: All datetimes stored in UTC in the database
- **Display**: All API responses show times in IST format
- **Conversion**: Automatic conversion between UTC and IST using pytz


