import api from './index.js'

export const getDocuments = (projectId) => api.get(`/projects/${projectId}/documents`)

export const uploadDocument = (projectId, file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/projects/${projectId}/documents`, formData)
}

export const downloadDocument = (projectId, docId) => {
  window.open(`/api/projects/${projectId}/documents/${docId}/download`, '_blank')
}

export const deleteDocument = (projectId, docId) =>
  api.delete(`/projects/${projectId}/documents/${docId}`)
