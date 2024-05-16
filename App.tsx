import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import './FitTrack.css';

const FitTrack: React.FC = () => {
  const [activityLogs, setActivityLogs] = useState<Array<any>>([]);
  const [nutritionInfo, setNutritionInfo] = useState<Array<any>>([]);
  const [fitnessGoals, setFitnessGoals] = useState({ calorieTarget: 2000, stepTarget: 10000, waterTargetLiters: 2 });
  const [preferences, setPreferences] = useState({ colorScheme: 'light', enableNotifications: true });

  const fetchActivityData = async () => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/daily-activity`);
    const data = await response.json();
    setActivityLogs(data);
  };

  const fetchNutritionData = async () => {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/diet`);
    const data = await response.json();
    setNutritionInfo(data);
  };

  useEffect(() => {
    fetchActivityData();
    fetchNutritionData();
  }, []);

  const updateGoals = (newFitnessGoals: any) => {
    setFitnessGoals(newFitnessGoals);
  };

  const updatePreferences = (newPreferences: any) => {
    setPreferences(newPreferences);
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
        <LineChart width={600} height={300} data={activityLogs}>
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