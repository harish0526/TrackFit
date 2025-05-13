from app import app, db, Exercise

def add_default_exercises():
    with app.app_context():
        # Check if exercises already exist
        if Exercise.query.first():
            print("Exercises already exist in the database.")
            return

        # Default exercises to add
        default_exercises = [
            ('Bench Press', 'Classic chest exercise performed on a flat bench', 'Chest'),
            ('Squat', 'Compound leg exercise targeting quadriceps, hamstrings, and glutes', 'Legs'),
            ('Deadlift', 'Full body compound exercise focusing on posterior chain', 'Back'),
            ('Pull-up', 'Upper body exercise targeting back and biceps', 'Back'),
            ('Push-up', 'Bodyweight exercise for chest, shoulders, and triceps', 'Chest'),
            ('Plank', 'Core stability exercise', 'Core'),
            ('Running', 'Cardiovascular exercise', 'Cardio'),
            ('Cycling', 'Low-impact cardiovascular exercise', 'Cardio'),
            ('Shoulder Press', 'Overhead press targeting deltoids', 'Shoulders'),
            ('Bicep Curl', 'Isolation exercise for biceps', 'Arms'),
            ('Tricep Extension', 'Isolation exercise for triceps', 'Arms'),
            ('Leg Press', 'Machine exercise for lower body', 'Legs'),
            ('Lunges', 'Unilateral leg exercise', 'Legs'),
            ('Romanian Deadlift', 'Hip hinge exercise focusing on hamstrings', 'Back'),
            ('Lat Pulldown', 'Back exercise targeting lats', 'Back')
        ]

        # Add exercises to database
        for name, description, category in default_exercises:
            exercise = Exercise(name=name, description=description, category=category)
            db.session.add(exercise)
            print(f"Adding exercise: {name}")

        # Commit changes
        db.session.commit()
        print("\nSuccessfully added default exercises to the database!")

if __name__ == '__main__':
    add_default_exercises() 