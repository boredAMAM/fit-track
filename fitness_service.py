from flask import Flask, request, jsonify
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy

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
    new_session = WorkoutSession(duration_minutes=data['duration_minutes'], activity_type=data['activity_type'], user_id=data['user_id'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({'message': 'Workout session added'}), 201

@app.route('/diet', methods=['POST'])
def add_diet():
    data = request.get_json()
    new_diet = DietaryIntake(meal_type=data['meal_type'], description=data['description'], calories=data['calories'], user_id=data['user_id'])
    db.session.add(new_diet)
    db.session.commit()
    return jsonify({'message': 'Dietary intake added'}), 201

@app.route('/stats/<int:user_id>', methods=['GET'])
def get_stats(user_id):
    workouts = WorkoutSession.query.filter_by(user_id=user_id).all()
    diets = DietaryIntake.query.filter_by(user_id=user_id).all()
    
    total_calories = sum(diet.calories for diet in diets)
    total_duration = sum(workout.duration_minutes for workout in workouts)
    
    return jsonify({
        'total_calories_consumed': total_calories,
        'total_workout_duration': total_duration
    })

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', 5000))