'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { apiService } from '@/services/api';
import ProtectedRoute from '@/components/ProtectedRoute';
import Navbar from '@/components/Navbar';
import { Project, Task, CreateTaskData } from '@/types/api';
import Link from 'next/link';

export default function ProjectDetailPage() {
  const { id } = useParams();
  const [project, setProject] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [taskFormData, setTaskFormData] = useState<Partial<CreateTaskData>>({
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    deadline: ''
  });
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const fetchProjectDetails = async () => {
      try {
        const projectId = Array.isArray(id) ? parseInt(id[0], 10) : parseInt(id as string, 10);
        const projectData = await apiService.getProjectById(projectId);
        const tasksData = await apiService.getTasksByProject(projectId);
        
        setProject(projectData);
        setTasks(tasksData);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch project details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProjectDetails();
    }
  }, [id]);

  const handleTaskChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setTaskFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateTaskForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!taskFormData.title?.trim()) {
      errors.title = 'Title is required';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateTaskForm() || !project) {
      return;
    }

    try {
      const taskData = {
        ...taskFormData,
        project: project.id
      } as CreateTaskData;
      
      const newTask = await apiService.createTask(taskData);
      setTasks([...tasks, newTask]);
      setTaskFormData({ 
        title: '', 
        description: '', 
        status: 'todo', 
        priority: 'medium', 
        deadline: '' 
      });
      setShowTaskForm(false);
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    }
  };

  const handleStatusChange = async (taskId: number, newStatus: string) => {
    try {
      const updatedTask = await apiService.updateTaskStatus(taskId, newStatus);
      setTasks(tasks.map(task => 
        task.id === taskId ? updatedTask : task
      ));
    } catch (err: any) {
      setError(err.message || 'Failed to update task status');
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="animate-pulse">
                <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
                <div className="bg-white shadow rounded-lg p-6 mb-6">
                  <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                </div>
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-16 bg-gray-200 rounded-lg"></div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (!project) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-100">
          <Navbar />
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <span className="block sm:inline">Project not found</span>
              </div>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mb-6">
              <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
                <Link 
                  href="/projects" 
                  className="text-indigo-600 hover:text-indigo-900"
                >
                  ← Back to Projects
                </Link>
              </div>
              <p className="mt-2 text-gray-600">{project.description}</p>
            </div>

            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
                <span className="block sm:inline">{error}</span>
              </div>
            )}

            {/* Project Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-blue-500 rounded-md p-3">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Progress</dt>
                        <dd className="flex items-baseline">
                          <div className="text-2xl font-semibold text-gray-900">{project.progress_percentage}%</div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-green-500 rounded-md p-3">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Completed Tasks</dt>
                        <dd className="flex items-baseline">
                          <div className="text-2xl font-semibold text-gray-900">
                            {tasks.filter(t => t.status === 'completed').length}
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 bg-yellow-500 rounded-md p-3">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Remaining Tasks</dt>
                        <dd className="flex items-baseline">
                          <div className="text-2xl font-semibold text-gray-900">
                            {tasks.filter(t => t.status !== 'completed').length}
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Tasks Section */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
              <div className="px-4 py-5 sm:px-6 border-b border-gray-200 flex justify-between items-center">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Tasks</h3>
                <button
                  onClick={() => setShowTaskForm(!showTaskForm)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  {showTaskForm ? 'Cancel' : '+ Add Task'}
                </button>
              </div>

              {showTaskForm && (
                <div className="p-6 border-b border-gray-200">
                  <h4 className="text-md font-medium text-gray-900 mb-4">Create New Task</h4>
                  <form onSubmit={handleTaskSubmit}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                          Title *
                        </label>
                        <input
                          type="text"
                          id="title"
                          name="title"
                          value={taskFormData.title || ''}
                          onChange={handleTaskChange}
                          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${
                            formErrors.title ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-indigo-500'
                          }`}
                          placeholder="Task title"
                        />
                        {formErrors.title && (
                          <p className="mt-1 text-sm text-red-600">{formErrors.title}</p>
                        )}
                      </div>
                      <div>
                        <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                          Priority
                        </label>
                        <select
                          id="priority"
                          name="priority"
                          value={taskFormData.priority || 'medium'}
                          onChange={handleTaskChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="low">Low</option>
                          <option value="medium">Medium</option>
                          <option value="high">High</option>
                          <option value="urgent">Urgent</option>
                        </select>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                          Status
                        </label>
                        <select
                          id="status"
                          name="status"
                          value={taskFormData.status || 'todo'}
                          onChange={handleTaskChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="review">Review</option>
                          <option value="completed">Completed</option>
                        </select>
                      </div>
                      <div>
                        <label htmlFor="deadline" className="block text-sm font-medium text-gray-700 mb-1">
                          Deadline
                        </label>
                        <input
                          type="datetime-local"
                          id="deadline"
                          name="deadline"
                          value={taskFormData.deadline || ''}
                          onChange={handleTaskChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                      </div>
                    </div>
                    <div className="mb-4">
                      <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        id="description"
                        name="description"
                        value={taskFormData.description || ''}
                        onChange={handleTaskChange}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="Task description"
                      ></textarea>
                    </div>
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                      >
                        Create Task
                      </button>
                    </div>
                  </form>
                </div>
              )}

              <ul className="divide-y divide-gray-200">
                {tasks.map((task) => (
                  <li key={task.id} className="px-4 py-4 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={task.status === 'completed'}
                          onChange={() => 
                            handleStatusChange(
                              task.id, 
                              task.status === 'completed' ? 'todo' : 'completed'
                            )
                          }
                          className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                        />
                        <div className="ml-3">
                          <p className={`text-sm font-medium ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                            {task.title}
                          </p>
                          <p className="text-sm text-gray-500 truncate max-w-xs">{task.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          task.status === 'completed' ? 'bg-green-100 text-green-800' :
                          task.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                          task.status === 'review' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {task.status.replace('_', ' ')}
                        </span>
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          task.priority === 'low' ? 'bg-green-100 text-green-800' :
                          task.priority === 'medium' ? 'bg-blue-100 text-blue-800' :
                          task.priority === 'high' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {task.priority}
                        </span>
                        {task.deadline && (
                          <span className="text-xs text-gray-500">
                            {new Date(task.deadline).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
                {tasks.length === 0 && (
                  <li>
                    <div className="px-4 py-12 text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
                      <p className="mt-1 text-sm text-gray-500">Get started by creating a new task.</p>
                    </div>
                  </li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}