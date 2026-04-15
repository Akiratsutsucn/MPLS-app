import api from './index.js'

export const getUpcoming = () => api.get('/dashboard/upcoming')
