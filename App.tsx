import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import './FitTrack.css';

const FitTrack: React.FC = () => {
  const [dailyActivity, setDailyActivity] = useState<Array<any>>([]);
  const [diet, setDiet] = useState<Array<any>>([]);
  const [goals, setGoals] = useState({ calorieIntake: 2000, steps: 10000, waterIntake: 2 });
  const [userPreferences, setUserPreferences] = useState({ theme: 'light', notifications: true });

  const fetchDailyActivity = async () => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/daily-activity`);
    const data = await response.json();
    setDailyActivity(data);
  };

  const fetchDiet = async () => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/diet`);
    const data = await response.json();
    setDiet(data);
  };

  useEffect(() => {
    fetchDailyActivity();
    fetchDiet();
  }, []);

  const handleGoalChange = (newGoals: any) => {
    setGoals(newGoals);
  };

  const handleUserPreferencesChange = (newPreferences: any) => {
    setUserPreferences(newPreferences);
  };

  return (
    <div className="fitTrack">
      <h1>FitTrack Dashboard</h1>

      <section className="userSettings">
        <h2>User Settings</h2>
      </section>

      <section className="dailyActivity">
        <h2>Daily Activity</h2>
      </section>

      <section className="dietTracking">
        <h2>Diet Tracking</h2>
      </section>

      <section className="progressVisualization">
        <h2>Progress Visualization</h2>
        <LineChart width={600} height={300} data={dailyActivity}>
          <Line type="monotone" dataKey="steps" stroke="#8884d8" />
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
        </LineChart>
      </section>

    </div>
  );
};

export default FitTrack;