import api from './index.js'

export const getProjects = (params) => api.get('/projects', { params })
export const createProject = (data) => api.post('/projects', data)
export const getProject = (id) => api.get(`/projects/${id}`)
export const updateProject = (id, data) => api.put(`/projects/${id}`, data)
export const deleteProject = (id) => api.delete(`/projects/${id}`)
export const updatePhase = (id, phase) => api.patch(`/projects/${id}/phase`, { phase })
