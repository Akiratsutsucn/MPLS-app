import api from './index.js'

export const exportReport = async (projectId) => {
  const response = await api.get(`/projects/${projectId}/export`, { responseType: 'blob' })
  const url = URL.createObjectURL(response.data)
  const a = document.createElement('a')
  a.href = url
  a.download = `project-${projectId}-report.docx`
  a.click()
  URL.revokeObjectURL(url)
}
