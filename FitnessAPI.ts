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

interface FetchLogsOptions {
  userId: number;
  startDate?: string;
  endDate?: string;
}

class SimpleCache {
  private cache: Map<string, any>;

  constructor() {
    this.cache = new Map<string, any>();
  }

  get(key: string) {
    return this.cache.get(key);
  }

  has(key: string): boolean {
    return this.cache.has(key);
  }

  set(key: string, value: any) {
    this.cache.set(key, value);
  }
}

const apiCache = new SimpleCache();

const apiModule = {
  async fetchFitnessLogs({ userId, startDate, endDate }: FetchLogsOptions) {
    try {
      const cacheKey = `fitness-logs-${userId}-${startDate}-${endDate}`;
      if (apiCache.has(cacheKey)) {
        console.log('Serving from cache');
        return apiCache.get(cacheKey);
      }

      const params = startDate && endDate ? { startDate, endDate } : {};
      const response = await axios.get(`${apiUrl}/fitness-logs/${userId}`, { params });

      apiCache.set(cacheKey, response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching fitness logs', error);
      throw error;
    }
  },

  async createFitnessLog(fitnessLog: FitnessLog) {
    // Invalidate cache when a new log is created
    const cacheKey = `fitness-logs-${fitnessLog.userId}-`;
    // A simplistic approach to invalidate related cache keys
    [...apiCache.cache.keys()].forEach(key => {
      if (key.startsWith(cacheKey)) {
        apiCache.cache.delete(key);
      }
    });

    try {
      const response = await axios.post(`${apiUrl}/fitness-logs`, fitnessLog);
      return response.data;
    } catch (error) {
      console.error('Error creating fitness log', error);
      throw error;
    }
  },

  // Similar implementations for updateFitnessLog, fetchDietaryLogs, createDietaryLog,
  // updateDietaryLog, and fetchProgressReports follow, considering cache invalidation on updates.
};

export default apiModule;