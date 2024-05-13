from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os
from flask_sqlalchemy import SQLAlchemy
from functools import lru_cache

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getenv("DATABASE_PATH", "fittrack.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    workouts = db.relationship('WorkoutSession', backref='user', lazy=True)
    diets = db.relationship('DietaryIntake', backref='user', lazy=True)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer, nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DietaryIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    meal_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/workout', methods=['POST'])
def add_workout():
    data = request.get_json()
    new_session = WorkoutSession(
        duration_minutes=data['duration_minutes'], 
        activity_type=data['activity_type'], 
        user_id=data['user_id']
    )
    db.session.add(new_session)
    db.session.commit()
    _clear_cache(user_id=data['user_id'])  # Clear cache for this user
    return jsonify({'message': 'Workout session added'}), 201

@app.route('/workout/<int:session_id>', methods=['PUT'])
def update_workout(session_id):
    data = request.get_json()
    session = WorkoutSession.query.get(session_id)
    if not session:
        return jsonify({'message': 'Session not found'}), 404

    session.duration_minutes = data.get('duration_minutes', session.duration_minutes)
    session.activity_type = data.get('activity_type', session.activity_type)
    db.session.commit()
    _clear_cache(user_id=session.user_id)  # Clear cache for this user
    return jsonify({'message': 'Workout session updated'}), 200

@app.route('/diet', methods=['POST'])
def add_diet():
    data = request.get_json()
    new_diet = DietaryIntake(
        meal_type=data['meal_type'], 
        description=data['description'], 
        calories=data['calories'], 
        user_id=data['user_id']
    )
    db.session.add(new_diet)
    db.session.commit()
    _clear_cache(user_id=data['user_id'])  # Clear cache for this user
    return jsonify({'message': 'Dietary intake added'}), 201

@app.route('/diet/<int:diet_id>', methods=['PUT'])
def update_diet(diet_id):
    data = request.get_json()
    diet = DietaryIntake.query.get(diet_id)
    if not diet:
        return jsonify({'message': 'Diet not found'}), 404

    diet.meal_type = data.get('meal_type', diet.meal_type)
    diet.description = data.get('description', diet.description)
    diet.calories = data.get('calories', diet.calories)
    db.session.commit()
    _clear_cache(user_id=diet.user_id)  # Clear cache for this user
    return jsonify({'message': 'Dietary intake updated'}), 200

@lru_cache(maxsize=32)
def _get_stats_cached(user_id):
    workouts = WorkoutSession.query.filter_by(user_id=user_id).all()
    diets = DietaryIntake.query.filter_by(user_id=user_id).all()

    total_calories = sum(diet.calories for diet in diets)
    total_duration = sum(workout.duration_minutes for workout in workouts)

    return {
        'total_calories_consumed': total_calories,
        'total_workout_duration': total_duration
    }

def _clear_cache(user_id):
    _get_stats_cached.cache_clear()

@app.route('/stats/<int:user_id>', methods=['GET'])
def get_stats(user_id):
    stats = _get_stats_cached(user_id)
    return jsonify(stats)

@app.route('/stats/date_range/<int:user_id>', methods=['POST'])
def date_range_stats(user_id):
    data = request.get_json()
    start_date = datetime.strptime(data['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(data['end_date'], "%Y-%m-%d")

    workouts = WorkoutSession.query.filter(
        WorkoutSession.user_id == user_id,
        WorkoutSession.date >= start_date,
        WorkoutSession.date <= end_date
    ).all()

    diets = DietaryIntake.query.filter(
        DietaryIntake.user_id == user_id,
        DietaryIntake.date >= start_date,
        DietaryIntake.date <= end_date
    ).all()

    total_calories = sum(diet.calories for diet in diets)
    total_duration = sum(workout.duration_minutes for workout in workouts)

    stats = {
        'total_calories_consumed': total_calories,
        'total_workout_duration': total_duration
    }

    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', 5000))