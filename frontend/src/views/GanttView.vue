<template>
  <div class="gantt-page">
    <NavBar @create="showCreateDialog = true" @search="handleSearch" />

    <main class="gantt-main">
      <div class="gantt-toolbar">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="day">日视图</el-radio-button>
          <el-radio-button value="week">周视图</el-radio-button>
          <el-radio-button value="month">月视图</el-radio-button>
        </el-radio-group>
        <span class="gantt-hint">点击项目条查看详情</span>
      </div>
      <div class="gantt-container">
        <div v-if="ganttTasks.length === 0" class="gantt-empty">
          <el-empty description="暂无可显示的项目（需设置开始日期和截止日期）" />
        </div>
        <div v-show="ganttTasks.length > 0" ref="chartRef" class="gantt-chart"></div>
      </div>
    </main>

    <!-- Create project dialog -->
    <el-dialog v-model="showCreateDialog" title="新建项目" width="520px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select v-model="form.assignee_id" placeholder="请选择负责人" clearable style="width: 100%">
            <el-option v-for="u in users" :key="u.id" :label="u.name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="form.start_date"
            type="date"
            placeholder="请选择开始日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="截止日期" prop="deadline">
          <el-date-picker
            v-model="form.deadline"
            type="date"
            placeholder="请选择截止日期"
            style="width: 100%"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="备注（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- Detail drawer -->
    <ProjectDetail
      v-if="detailProject"
      :project-id="detailProject.id"
      @close="detailProject = null"
      @updated="onProjectUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import NavBar from '../components/NavBar.vue'
import ProjectDetail from '../components/ProjectDetail.vue'
import { PHASES, LEVELS, PHASE_MAP } from '../utils/constants.js'
import { useProjectsStore } from '../stores/projects.js'
import { getUsers } from '../api/auth.js'

const projectsStore = useProjectsStore()

const searchQuery = ref('')
const showCreateDialog = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const detailProject = ref(null)
const chartRef = ref(null)
const viewMode = ref('month')
const users = ref([])

let chart = null

const form = ref({
  name: '',
  assignee_id: null,
  start_date: '',
  deadline: '',
  notes: '',
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

const filteredProjects = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return projectsStore.projects
  return projectsStore.projects.filter(
    (p) => p.name?.toLowerCase().includes(q) || p.system_name?.toLowerCase().includes(q),
  )
})

const ganttTasks = computed(() => {
  return filteredProjects.value
    .filter((p) => p.start_date && p.deadline)
    .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
})

function handleSearch(q) {
  searchQuery.value = q
}

function getTimeRange() {
  if (ganttTasks.value.length === 0) return { min: null, max: null }
  const starts = ganttTasks.value.map((p) => new Date(p.start_date).getTime())
  const ends = ganttTasks.value.map((p) => new Date(p.deadline).getTime())
  const min = Math.min(...starts)
  const max = Math.max(...ends)
  const pad = (max - min) * 0.05 || 86400000 * 7
  return { min: min - pad, max: max + pad }
}

function renderChart() {
  if (!chartRef.value || ganttTasks.value.length === 0) return

  if (!chart) {
    chart = echarts.init(chartRef.value)
    chart.on('click', (params) => {
      if (params.componentType === 'series') {
        const project = ganttTasks.value[params.dataIndex]
        if (project) detailProject.value = project
      }
    })
  }

  const projects = ganttTasks.value
  const categories = projects.map((p) => p.name)
  const { min, max } = getTimeRange()

  // Build bar data: each bar is [start, end] on the time axis
  const barData = projects.map((p) => {
    const phase = PHASE_MAP[p.phase]
    const start = new Date(p.start_date).getTime()
    const end = new Date(p.deadline).getTime()
    return {
      value: [start, end],
      itemStyle: {
        color: phase?.color || '#409EFF',
        borderRadius: [3, 3, 3, 3],
      },
    }
  })

  // Progress overlay
  const progressData = projects.map((p) => {
    const start = new Date(p.start_date).getTime()
    const end = new Date(p.deadline).getTime()
    const progress = (p.checklist_completion || 0) / 100
    const progressEnd = start + (end - start) * progress
    return {
      value: [start, progressEnd],
      itemStyle: {
        color: 'rgba(255,255,255,0.3)',
        borderRadius: [3, 3, 3, 3],
      },
    }
  })

  const axisInterval = viewMode.value === 'day' ? 86400000 : viewMode.value === 'week' ? 86400000 * 7 : 86400000 * 30

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.componentType !== 'series') return ''
        const p = projects[params.dataIndex]
        const phase = PHASE_MAP[p.phase]
        const start = new Date(p.start_date).toLocaleDateString('zh-CN')
        const end = new Date(p.deadline).toLocaleDateString('zh-CN')
        const progress = Math.round(p.checklist_completion || 0)
        return `<b>${p.name}</b><br/>阶段：${phase?.label || p.phase}<br/>时间：${start} ~ ${end}<br/>进度：${progress}%`
      },
    },
    grid: {
      left: 160,
      right: 40,
      top: 30,
      bottom: 40,
    },
    xAxis: {
      type: 'time',
      min,
      max,
      axisLabel: {
        formatter: (val) => {
          const d = new Date(val)
          return `${d.getMonth() + 1}/${d.getDate()}`
        },
      },
      splitLine: { show: true, lineStyle: { type: 'dashed', color: '#eee' } },
    },
    yAxis: {
      type: 'category',
      data: categories,
      inverse: true,
      axisLabel: {
        width: 140,
        overflow: 'truncate',
        fontSize: 12,
      },
    },
    series: [
      {
        type: 'custom',
        renderItem: (params, api) => {
          const categoryIndex = api.value(2)
          const start = api.coord([api.value(0), categoryIndex])
          const end = api.coord([api.value(1), categoryIndex])
          const height = 22
          const style = api.style()
          return {
            type: 'rect',
            shape: {
              x: start[0],
              y: start[1] - height / 2,
              width: Math.max(end[0] - start[0], 4),
              height,
              r: [3, 3, 3, 3],
            },
            style,
          }
        },
        encode: { x: [0, 1], y: 2 },
        data: projects.map((p, i) => {
          const phase = PHASE_MAP[p.phase]
          return {
            value: [
              new Date(p.start_date).getTime(),
              new Date(p.deadline).getTime(),
              i,
            ],
            itemStyle: { color: phase?.color || '#409EFF' },
          }
        }),
      },
    ],
  }

  // Dynamic height based on number of projects
  const chartHeight = Math.max(300, projects.length * 42 + 80)
  chartRef.value.style.height = chartHeight + 'px'
  chart.resize()
  chart.setOption(option, true)
}

async function onProjectUpdated() {
  await projectsStore.fetchProjects()
  await nextTick()
  renderChart()
}

async function submitCreate() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await projectsStore.createProject({ ...form.value })
    showCreateDialog.value = false
    form.value = { name: '', assignee_id: null, start_date: '', deadline: '', notes: '' }
    ElMessage.success('项目创建成功')
    await nextTick()
    renderChart()
  } catch {
    ElMessage.error('创建失败，请重试')
  } finally {
    submitting.value = false
  }
}

watch([ganttTasks, viewMode], () => {
  nextTick(() => renderChart())
})

let resizeHandler = null

onMounted(async () => {
  await projectsStore.fetchProjects()
  try { users.value = (await getUsers()).data } catch {}
  await nextTick()
  renderChart()
  resizeHandler = () => chart?.resize()
  window.addEventListener('resize', resizeHandler)
})

onUnmounted(() => {
  if (resizeHandler) window.removeEventListener('resize', resizeHandler)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.gantt-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
  overflow: hidden;
  padding-top: 56px;
}

.gantt-main {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.gantt-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.gantt-hint {
  font-size: 12px;
  color: #909399;
}

.gantt-container {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  min-height: 300px;
}

.gantt-chart {
  width: 100%;
  min-height: 300px;
}

.gantt-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
