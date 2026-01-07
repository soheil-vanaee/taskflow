// User types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: 'owner' | 'member';
  date_joined: string;
  created_at: string;
  updated_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

// Project types
export interface Project {
  id: number;
  name: string;
  description: string;
  deadline?: string;
  owner: string; // email
  members: number[]; // user IDs
  created_at: string;
  updated_at: string;
  progress_percentage: number;
}

export interface ProjectListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Project[];
}

export interface CreateProjectData {
  name: string;
  description: string;
  deadline?: string;
  members?: number[];
}

// Task types
export interface Task {
  id: number;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'review' | 'completed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  deadline?: string;
  project: number; // project ID
  assignee?: number; // user ID
  dependencies: number[]; // task IDs
  created_at: string;
  updated_at: string;
  assignee_details?: {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
  };
  project_details?: {
    id: number;
    name: string;
    owner: string;
  };
}

export interface TaskListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Task[];
}

export interface CreateTaskData {
  title: string;
  description: string;
  status?: 'todo' | 'in_progress' | 'review' | 'completed';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  deadline?: string;
  project: number;
  assignee?: number;
  dependencies?: number[];
}

// Subscription types
export interface SubscriptionPlan {
  id: number;
  name: string;
  description: string;
  price: number;
  projects_limit: number;
  team_members_limit: number;
  tasks_limit: number;
  features: string[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserSubscription {
  id: number;
  user: number;
  plan: SubscriptionPlan;
  plan_id: number;
  status: 'active' | 'trialing' | 'cancelled' | 'past_due';
  start_date: string;
  end_date?: string;
  trial_end_date?: string;
  auto_renew: boolean;
  stripe_subscription_id?: string;
  is_active_subscription: boolean;
  days_until_expiry?: number;
  is_trial_period: boolean;
  created_at: string;
  updated_at: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}