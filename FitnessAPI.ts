import axios from 'axios';

const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:3000';

interface FitnessLog {
  id?: number;
  userId: number;
  date: string;
  type: string;
  duration: number;
  intensity: string;
}

interface DietaryLog {
  id?: number;
  userId: number;
  date: string;
  mealType: string;
  calories: number;
}

interface ProgressReport {
  userId: number;
  startDate: string;
  endDate: string;
}

interface FetchLogsOptions {
  userId: number;
  startDate?: string;
  endDate?: string;
}

const apiModule = {
  async fetchFitnessLogs({ userId, startDate, endDate }: FetchLogsOptions) {
    try {
      const params = startDate && endDate ? { startDate, endDate } : {};
      const response = await axios.get(`${apiUrl}/fitness-logs/${userId}`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching fitness logs', error);
      throw error;
    }
  },

  async createFitnessLog(fitnessLog: FitnessLog) {
    try {
      const response = await axios.post(`${apiUrl}/fitness-logs`, fitnessLog);
      return response.data;
    } catch (error) {
      console.error('Error creating fitness log', error);
      throw error;
    }
  },

  async updateFitnessLog(fitnessLog: FitnessLog) {
    try {
      const { id } = fitnessLog;
      if (!id) throw new Error('Fitness log ID is required for update.');
      const response = await axios.put(`${apiUrl}/fitness-logs/${id}`, fitnessLog);
      return response.data;
    } catch (error) {
      console.error('Error updating fitness log', error);
      throw error;
    }
  },

  async fetchDietaryLogs({ userId, startDate, endDate }: FetchLogsOptions) {
    try {
      const params = startDate && endDate ? { startDate, endDate } : {};
      const response = await axios.get(`${apiUrl}/dietary-logs/${userId}`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching dietary logs', error);
      throw error;
    }
  },
  
  async createDietaryLog(dietaryLog: DietaryLog) {
    try {
      const response = await axios.post(`${apiUrl}/dietary-logs`, dietaryLog);
      return response.data;
    } catch (error) {
      console.error('Error creating dietary log', error);
      throw error;
    }
  },

  async updateDietaryLog(dietaryLog: DietaryLog) {
    try {
      const { id } = dietaryLog;
      if (!id) throw new Error('Dietary log ID is required for update.');
      const response = await axios.put(`${apiUrl}/dietary-logs/${id}`, dietaryLog);
      return response.data;
    } catch (error) {
      console.error('Error updating dietary log', error);
      throw error;
    }
  },

  async fetchProgressReports(params: ProgressReport) {
    try {
      const response = await axios.get(`${apiUrl}/progress-reports`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching progress reports', error);
      throw error;
    }
  },
};

export default apiModule;