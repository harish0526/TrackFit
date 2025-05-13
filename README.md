# TrackFit - Fitness Tracking Website

A web-based fitness tracking application that allows users to log workouts and track their progress over time.

## Features
- User authentication (login/signup)
- Workout logging
- Exercise tracking
- Progress visualization
- Personal records management

## Setup Instructions

1. Make sure XAMPP is installed and running (Apache and MySQL services)
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create the database:
   - Open phpMyAdmin (http://localhost/phpmyadmin)
   - Create a new database named 'trackfit'
   - Import the schema from `database/schema.sql`

6. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the database credentials if needed

7. Run the application:
   ```
   python app.py
   ```

8. Access the website at http://localhost:5000

## Project Structure
```
trackfit/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   └── templates/
├── database/
│   └── schema.sql
├── .env.example
├── app.py
├── requirements.txt
└── README.md
``` 