import { defineStore } from 'pinia'
import * as projectsApi from '../api/projects.js'

export const useProjectsStore = defineStore('projects', {
  state: () => ({
    projects: [],
    currentProject: null,
    loading: false,
  }),

  getters: {
    projectsByPhase: (state) => {
      return state.projects.reduce((acc, project) => {
        const phase = project.phase || 'unknown'
        if (!acc[phase]) acc[phase] = []
        acc[phase].push(project)
        return acc
      }, {})
    },
  },

  actions: {
    async fetchProjects(params) {
      this.loading = true
      try {
        const res = await projectsApi.getProjects(params)
        this.projects = res.data.items || res.data
      } finally {
        this.loading = false
      }
    },

    async fetchProject(id) {
      this.loading = true
      try {
        const res = await projectsApi.getProject(id)
        this.currentProject = res.data
      } finally {
        this.loading = false
      }
    },

    async createProject(data) {
      const res = await projectsApi.createProject(data)
      this.projects = [...this.projects, res.data]
      return res.data
    },

    async updateProject(id, data) {
      const res = await projectsApi.updateProject(id, data)
      this.projects = this.projects.map((p) => (p.id === id ? res.data : p))
      if (this.currentProject?.id === id) this.currentProject = res.data
      return res.data
    },

    async deleteProject(id) {
      await projectsApi.deleteProject(id)
      this.projects = this.projects.filter((p) => p.id !== id)
    },

    async updatePhase(id, phase) {
      const res = await projectsApi.updatePhase(id, phase)
      this.projects = this.projects.map((p) => (p.id === id ? res.data : p))
      if (this.currentProject?.id === id) this.currentProject = res.data
      return res.data
    },
  },
})
