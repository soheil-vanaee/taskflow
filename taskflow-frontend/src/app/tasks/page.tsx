'use client';

import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';
import ProtectedRoute from '@/components/ProtectedRoute';
import Navbar from '@/components/Navbar';
import { Task, CreateTaskData } from '@/types/api';

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<Partial<CreateTaskData>>({
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
    project: 1 // Default to first project
  });
  const [projects, setProjects] = useState<{id: number, name: string}[]>([]);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const tasksData = await apiService.getTasks();
        const projectsData = await apiService.getProjects();
        
        setTasks(tasksData);
        setProjects(projectsData.map(p => ({ id: p.id, name: p.name })));
      } catch (err: any) {
        setError(err.message || 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};
    if (!formData.title?.trim()) {
      errors.title = 'Title is required';
    }
    if (!formData.project) {
      errors.project = 'Project is required';
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      const newTask = await apiService.createTask(formData as CreateTaskData);
      setTasks([...tasks, newTask]);
      setFormData({ 
        title: '', 
        description: '', 
        status: 'todo', 
        priority: 'medium',
        project: projects[0]?.id || 1
      });
      setShowForm(false);
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

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <div className="py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="mb-6">
              <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
                <button
                  onClick={() => setShowForm(!showForm)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                >
                  {showForm ? 'Cancel' : '+ Add Task'}
                </button>
              </div>
              <p className="mt-2 text-gray-600">Manage your tasks and track progress.</p>
            </div>

            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
                <span className="block sm:inline">{error}</span>
              </div>
            )}

            {showForm && (
              <div className="bg-white shadow-md rounded-lg p-6 mb-8">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Create New Task</h2>
                <form onSubmit={handleSubmit}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                        Title *
                      </label>
                      <input
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title || ''}
                        onChange={handleChange}
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
                      <label htmlFor="project" className="block text-sm font-medium text-gray-700 mb-1">
                        Project *
                      </label>
                      <select
                        id="project"
                        name="project"
                        value={formData.project || ''}
                        onChange={handleChange}
                        className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 ${
                          formErrors.project ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 focus:ring-indigo-500'
                        }`}
                      >
                        <option value="">Select a project</option>
                        {projects.map(project => (
                          <option key={project.id} value={project.id}>
                            {project.name}
                          </option>
                        ))}
                      </select>
                      {formErrors.project && (
                        <p className="mt-1 text-sm text-red-600">{formErrors.project}</p>
                      )}
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                        Priority
                      </label>
                      <select
                        id="priority"
                        name="priority"
                        value={formData.priority || 'medium'}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                      </select>
                    </div>
                    <div>
                      <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                        Status
                      </label>
                      <select
                        id="status"
                        name="status"
                        value={formData.status || 'todo'}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        <option value="todo">To Do</option>
                        <option value="in_progress">In Progress</option>
                        <option value="review">Review</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                  </div>
                  <div className="mb-4">
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      id="description"
                      name="description"
                      value={formData.description || ''}
                      onChange={handleChange}
                      rows={3}
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

            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
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
                        {task.project_details && (
                          <span className="text-xs text-gray-500">
                            {task.project_details.name}
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