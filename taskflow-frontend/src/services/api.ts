import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { AuthResponse, LoginCredentials, RegisterData, Project, CreateProjectData, Task, CreateTaskData, SubscriptionPlan, UserSubscription } from '@/types/api';

const BACKEND_API_URL = process.env.BACKEND_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: BACKEND_API_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = this.getRefreshToken();
            if (refreshToken) {
              const response = await this.refreshToken(refreshToken);
              this.setTokens(response.data.access, response.data.refresh);
              
              originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            this.clearTokens();
            window.location.href = '/login';
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  private getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token');
    }
    return null;
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  private clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  private async refreshToken(refreshToken: string) {
    return this.client.post('/auth/token/refresh/', { refresh: refreshToken });
  }

  // Authentication methods
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login/', credentials);
    this.setTokens(response.data.access, response.data.refresh);
    return response.data;
  }

  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register/', userData);
    this.setTokens(response.data.access, response.data.refresh);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      const refreshToken = this.getRefreshToken();
      if (refreshToken) {
        await this.client.post('/auth/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      // Ignore logout errors
    } finally {
      this.clearTokens();
    }
  }

  async getProfile(): Promise<any> {
    const response = await this.client.get('/auth/profile/');
    return response.data;
  }

  // Project methods
  async getProjects(): Promise<Project[]> {
    const response = await this.client.get('/projects/');
    return response.data.results;
  }

  async getProjectById(id: number): Promise<Project> {
    const response = await this.client.get(`/projects/${id}/`);
    return response.data;
  }

  async createProject(projectData: CreateProjectData): Promise<Project> {
    const response = await this.client.post('/projects/', projectData);
    return response.data;
  }

  async updateProject(id: number, projectData: Partial<CreateProjectData>): Promise<Project> {
    const response = await this.client.put(`/projects/${id}/`, projectData);
    return response.data;
  }

  async deleteProject(id: number): Promise<void> {
    await this.client.delete(`/projects/${id}/`);
  }

  // Task methods
  async getTasks(): Promise<Task[]> {
    const response = await this.client.get('/tasks/');
    return response.data.results;
  }

  async getTasksByProject(projectId: number): Promise<Task[]> {
    const response = await this.client.get('/tasks/', { params: { project: projectId } });
    return response.data.results;
  }

  async getTaskById(id: number): Promise<Task> {
    const response = await this.client.get(`/tasks/${id}/`);
    return response.data;
  }

  async createTask(taskData: CreateTaskData): Promise<Task> {
    const response = await this.client.post('/tasks/', taskData);
    return response.data;
  }

  async updateTask(id: number, taskData: Partial<CreateTaskData>): Promise<Task> {
    const response = await this.client.put(`/tasks/${id}/`, taskData);
    return response.data;
  }

  async deleteTask(id: number): Promise<void> {
    await this.client.delete(`/tasks/${id}/`);
  }

  async updateTaskStatus(id: number, status: string): Promise<Task> {
    const response = await this.client.post(`/tasks/${id}/status/`, { status });
    return response.data;
  }

  // Subscription methods
  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    const response = await this.client.get('/subscriptions/plans/');
    return response.data;
  }

  async getUserSubscription(): Promise<UserSubscription> {
    const response = await this.client.get('/subscriptions/my-subscription/');
    return response.data;
  }

  async updateUserSubscription(planId: number): Promise<UserSubscription> {
    const response = await this.client.put('/subscriptions/my-subscription/', { plan_id: planId });
    return response.data;
  }

  async checkUsageLimits(): Promise<any> {
    const response = await this.client.get('/subscriptions/check-limits/');
    return response.data;
  }
}

export const apiService = new ApiService();

export default ApiService;