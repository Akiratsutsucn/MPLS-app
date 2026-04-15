import api from './index.js'

export const getChecklist = (projectId, phase) =>
  api.get(`/projects/${projectId}/checklist`, { params: phase ? { phase } : undefined })

export const toggleItem = (projectId, itemId, data) =>
  api.patch(`/projects/${projectId}/checklist/${itemId}`, data)

export const addItem = (projectId, data) =>
  api.post(`/projects/${projectId}/checklist`, data)

export const updateItem = (projectId, itemId, data) =>
  api.put(`/projects/${projectId}/checklist/${itemId}`, data)

export const deleteItem = (projectId, itemId) =>
  api.delete(`/projects/${projectId}/checklist/${itemId}`)
