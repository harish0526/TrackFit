from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from sqlalchemy import func

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/trackfit?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Changed from 'user' to 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    workouts = db.relationship('Workout', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Exercise(db.Model):
    __tablename__ = 'exercises'  # Changed from 'exercise' to 'exercises'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Workout(db.Model):
    __tablename__ = 'workouts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Changed from 'user' to 'users'
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    exercises = db.relationship('WorkoutExercise', backref='workout', lazy=True)

class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)  # Changed from 'exercise' to 'exercises'
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float)
    duration = db.Column(db.Integer)  # in seconds
    notes = db.Column(db.Text)
    exercise = db.relationship('Exercise')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        # Get the 5 most recent workouts for the current user
        recent_workouts = Workout.query.filter_by(user_id=current_user.id)\
            .order_by(Workout.date.desc())\
            .limit(5)\
            .all()
        return render_template('index.html', recent_workouts=recent_workouts)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()
    return render_template('dashboard.html', workouts=workouts, now=datetime.now().date())

@app.route('/workout/new', methods=['GET', 'POST'])
@login_required
def new_workout():
    if request.method == 'POST':
        try:
            # Create the workout
            workout = Workout(
                user_id=current_user.id,
                name=request.form.get('name'),
                date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
                duration=int(request.form.get('duration')) if request.form.get('duration') else None,
                notes=request.form.get('notes')
            )
            db.session.add(workout)
            db.session.flush()  # This gets us the workout ID

            # Get the exercise data from the form
            exercise_ids = request.form.getlist('exercise_id[]')
            sets = request.form.getlist('sets[]')
            reps = request.form.getlist('reps[]')
            weights = request.form.getlist('weight[]')

            # Validate that we have matching data for each exercise
            if not (len(exercise_ids) == len(sets) == len(reps) == len(weights)):
                raise ValueError("Mismatched exercise data")

            # Add each exercise to the workout
            for i in range(len(exercise_ids)):
                if exercise_ids[i]:  # Only add if an exercise was selected
                    try:
                        workout_exercise = WorkoutExercise(
                            workout_id=workout.id,
                            exercise_id=int(exercise_ids[i]),
                            sets=int(sets[i]),
                            reps=int(reps[i]),
                            weight=float(weights[i]) if weights[i] and weights[i].strip() else None
                        )
                        db.session.add(workout_exercise)
                    except (ValueError, TypeError) as e:
                        db.session.rollback()
                        flash(f'Error processing exercise data: {str(e)}')
                        return redirect(url_for('new_workout'))

            db.session.commit()
            flash('Workout saved successfully!')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving workout: {str(e)}')
            return redirect(url_for('new_workout'))
    
    # Get all exercises
    exercises = Exercise.query.all()
    
    # If no exercises exist, insert default exercises
    if not exercises:
        default_exercises = [
            ('Bench Press', 'Classic chest exercise performed on a flat bench', 'Chest'),
            ('Squat', 'Compound leg exercise targeting quadriceps, hamstrings, and glutes', 'Legs'),
            ('Deadlift', 'Full body compound exercise focusing on posterior chain', 'Back'),
            ('Pull-up', 'Upper body exercise targeting back and biceps', 'Back'),
            ('Push-up', 'Bodyweight exercise for chest, shoulders, and triceps', 'Chest'),
            ('Plank', 'Core stability exercise', 'Core'),
            ('Running', 'Cardiovascular exercise', 'Cardio'),
            ('Cycling', 'Low-impact cardiovascular exercise', 'Cardio')
        ]
        
        for name, description, category in default_exercises:
            exercise = Exercise(name=name, description=description, category=category)
            db.session.add(exercise)
        
        db.session.commit()
        exercises = Exercise.query.all()
    
    return render_template('new_workout.html', exercises=exercises)

@app.route('/progress')
@login_required
def progress():
    # Get workout statistics
    total_workouts = Workout.query.filter_by(user_id=current_user.id).count()
    
    # Get last 7 days of workouts
    seven_days_ago = datetime.now().date() - timedelta(days=7)
    recent_workouts = Workout.query.filter(
        Workout.user_id == current_user.id,
        Workout.date >= seven_days_ago
    ).order_by(Workout.date).all()
    
    # Prepare data for charts
    dates = []
    workout_counts = []
    total_duration = []
    
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
        workouts_on_day = [w for w in recent_workouts if w.date == date]
        workout_counts.append(len(workouts_on_day))
        total_duration.append(sum(w.duration or 0 for w in workouts_on_day))
    
    # Get most common exercises
    exercise_stats = db.session.query(
        Exercise.name,
        func.count(WorkoutExercise.id).label('count')
    ).join(WorkoutExercise).join(Workout).filter(
        Workout.user_id == current_user.id
    ).group_by(Exercise.name).order_by(func.count(WorkoutExercise.id).desc()).limit(5).all()
    
    # Get personal records
    personal_records = db.session.query(
        Exercise.name,
        func.max(WorkoutExercise.weight).label('max_weight'),
        func.max(WorkoutExercise.reps).label('max_reps')
    ).join(WorkoutExercise).join(Workout).filter(
        Workout.user_id == current_user.id,
        WorkoutExercise.weight.isnot(None)
    ).group_by(Exercise.name).all()
    
    return render_template('progress.html',
                         total_workouts=total_workouts,
                         dates=dates,
                         workout_counts=workout_counts,
                         total_duration=total_duration,
                         exercise_stats=exercise_stats,
                         personal_records=personal_records)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080) 