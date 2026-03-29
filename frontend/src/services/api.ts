/**
 * API 服务封装
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// 店铺管理 API
export const shopApi = {
  getCurrentShops: () => api.get('/shops/current'),
  saveCurrentShops: (data: any[]) => api.post('/shops/current', data),
  getHistoryShops: () => api.get('/shops/history'),
  saveHistoryShops: (data: any[]) => api.post('/shops/history', data),
  syncShops: () => api.post('/shops/sync'),
  importShops: (data: any[], target: 'current' | 'history') =>
    api.post('/shops/import', { data, target }),
};

// 模块管理 API
export const moduleApi = {
  getModules: () => api.get('/modules'),
  saveModules: (data: any[]) => api.post('/modules', data),
  uploadModule: (file: File, shopId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('shopId', shopId);
    return api.post('/modules/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// 任务管理 API
export const taskApi = {
  execute: (operation: string, params: any) =>
    api.post('/tasks/execute', { operation, params }),
  getHistory: () => api.get('/tasks/history'),
  getStatus: (taskId: string) => api.get(`/tasks/${taskId}/status`),
};

// 设置 API
export const settingsApi = {
  getSettings: () => api.get('/settings'),
  saveSettings: (data: any) => api.post('/settings', data),
  testWebhook: () => api.post('/settings/webhook/test'),
};

export default api;
