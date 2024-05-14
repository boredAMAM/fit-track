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

  invalidate(cacheKeyPrefix: string) {
    [...this.cache.keys()].forEach(key => {
      if (key.startsWith(cacheKeyPrefix)) {
        this.cache.delete(key);
      }
    });
  }
}

const apiCache = new SimpleCache();

const apiModule = {
  async fetchFitnessLogs(options: FetchLogsOptions) {
    try {
      const cacheKey = this.generateCacheKey('fitness-logs', options);
      if (apiCache.has(cacheKey)) {
        console.log('Serving from cache');
        return apiCache.get(cacheKey);
      }
      return await this.fetchAndCacheFitnessLogs(options, cacheKey);
    } catch (error) {
      console.error('Error fetching fitness logs', error);
      throw error;
    }
  },

  async createFitnessLog(fitnessLog: FitnessLog) {
    this.invalidateFitnessLogCache(fitnessLog.userId);

    try {
      const response = await axios.post(`${apiUrl}/fitness-logs`, fitnessLog);
      return response.data;
    } catch (error) {
      console.error('Error creating fitness log', error);
      throw error;
    }
  },

  generateCacheKey(prefix: string, { userId, startDate = '', endDate = '' }: FetchLogsOptions): string {
    return `${prefix}-${userId}-${startDate}-${endDate}`;
  },

  async fetchAndCacheFitnessLogs(options: FetchLogsOptions, cacheKey: string) {
    const params = options.startDate && options.endDate ? { startDate: options.startDate, endDate: options.endDate } : {};
    const response = await axios.get(`${apiUrl}/fitness-logs/${options.userId}`, { params });
    apiCache.set(cacheKey, response.data);
    return response.data;
  },

  invalidateFitnessLogCache(userId: number) {
    const cacheKey = `fitness-logs-${userId}-`;
    apiCache.invalidate(cacheKey);
  },
};

export default apiModule;