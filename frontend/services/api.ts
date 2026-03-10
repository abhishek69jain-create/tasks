import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.backendUrl + '/api' || 'https://quick-assign-1.preview.emergentagent.com/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  register: async (email: string, password: string, name: string, inviteCode?: string) => {
    const payload: any = { email, password, name };
    if (inviteCode) {
      payload.invite_code = inviteCode;
    }
    const response = await api.post('/auth/register', payload);
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const userService = {
  getUsers: async () => {
    const response = await api.get('/users');
    return response.data;
  },
};

export const taskService = {
  getTasks: async (filters?: any) => {
    const response = await api.get('/tasks', { params: filters });
    return response.data;
  },
  getTask: async (id: string) => {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },
  createTask: async (data: any) => {
    const response = await api.post('/tasks', data);
    return response.data;
  },
  updateTask: async (id: string, data: any) => {
    const response = await api.put(`/tasks/${id}`, data);
    return response.data;
  },
  deleteTask: async (id: string) => {
    const response = await api.delete(`/tasks/${id}`);
    return response.data;
  },
};

export const commentService = {
  getComments: async (taskId: string) => {
    const response = await api.get(`/tasks/${taskId}/comments`);
    return response.data;
  },
  createComment: async (taskId: string, text: string) => {
    const response = await api.post(`/tasks/${taskId}/comments`, { text });
    return response.data;
  },
};

export const attachmentService = {
  getAttachments: async (taskId: string) => {
    const response = await api.get(`/tasks/${taskId}/attachments`);
    return response.data;
  },
  uploadAttachment: async (taskId: string, file: any) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/tasks/${taskId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  downloadAttachment: async (attachmentId: string) => {
    const token = await AsyncStorage.getItem('token');
    return `${API_URL}/attachments/${attachmentId}/download?token=${token}`;
  },
};

export default api;