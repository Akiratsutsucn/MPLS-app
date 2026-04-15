import api from './index.js'

export const getReminders = (projectId) => api.get(`/projects/${projectId}/reminders`)
export const addReminder = (projectId, data) => api.post(`/projects/${projectId}/reminders`, data)
export const deleteReminder = (projectId, reminderId) =>
  api.delete(`/projects/${projectId}/reminders/${reminderId}`)
