import api from './index.js'

export const getLogs = (projectId) => api.get(`/projects/${projectId}/logs`)
export const addLog = (projectId, content) => api.post(`/projects/${projectId}/logs`, { content })
