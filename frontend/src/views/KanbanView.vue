<template>
  <div class="kanban-page">
    <NavBar @create="showCreateDialog = true" @search="handleSearch" />

    <main class="kanban-main">
      <div class="kanban-board">
        <div v-for="phase in PHASES" :key="phase.key" class="kanban-column">
          <!-- Column header -->
          <div class="column-header" :style="{ backgroundColor: phase.bgColor, borderTopColor: phase.color }">
            <span class="phase-icon">{{ phase.icon }}</span>
            <span class="phase-label">{{ phase.label }}</span>
            <el-badge :value="columnProjects(phase.key).length" class="phase-count" type="info" />
          </div>

          <!-- Draggable card list -->
          <draggable
            :list="columnProjects(phase.key)"
            group="projects"
            item-key="id"
            class="column-body"
            ghost-class="card-ghost"
            :data-phase="phase.key"
            @change="(evt) => onDragChange(evt, phase.key)"
          >
            <template #item="{ element }">
              <ProjectCard :project="element" @click="openDetail" />
            </template>
            <template #footer>
              <div v-if="columnProjects(phase.key).length === 0" class="empty-placeholder">
                暂无项目
              </div>
            </template>
          </draggable>
        </div>
      </div>
    </main>

    <!-- Create project dialog -->
    <el-dialog v-model="showCreateDialog" title="新建项目" width="520px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="系统名称" prop="system_name">
          <el-input v-model="form.system_name" placeholder="请输入系统名称" />
        </el-form-item>
        <el-form-item label="等保等级" prop="level">
          <el-select v-model="form.level" placeholder="请选择" style="width: 100%">
            <el-option v-for="(label, val) in LEVELS" :key="val" :label="label" :value="Number(val)" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户单位">
          <el-input v-model="form.client_org" placeholder="请输入客户单位" />
        </el-form-item>
        <el-form-item label="开始日期">
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
      @updated="projectsStore.fetchProjects()"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import draggable from 'vuedraggable'
import { ElMessage } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import ProjectCard from '../components/ProjectCard.vue'
import ProjectDetail from '../components/ProjectDetail.vue'
import { PHASES, LEVELS } from '../utils/constants.js'
import { useProjectsStore } from '../stores/projects.js'

const projectsStore = useProjectsStore()

const searchQuery = ref('')
const showCreateDialog = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const detailProject = ref(null)

const form = ref({
  name: '',
  system_name: '',
  level: null,
  client_org: '',
  start_date: '',
  deadline: '',
  notes: '',
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  system_name: [{ required: true, message: '请输入系统名称', trigger: 'blur' }],
  level: [{ required: true, message: '请选择等保等级', trigger: 'change' }],
}

const filteredProjects = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return projectsStore.projects
  return projectsStore.projects.filter(
    (p) =>
      p.name?.toLowerCase().includes(q) ||
      p.system_name?.toLowerCase().includes(q),
  )
})

function columnProjects(phaseKey) {
  return filteredProjects.value.filter((p) => p.phase === phaseKey)
}

function handleSearch(q) {
  searchQuery.value = q
}

function openDetail(project) {
  detailProject.value = project
}

async function onDragChange(evt, targetPhase) {
  if (evt.added) {
    const project = evt.added.element
    if (project.phase !== targetPhase) {
      await projectsStore.updatePhase(project.id, targetPhase)
    }
  }
}

async function submitCreate() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await projectsStore.createProject({ ...form.value })
    showCreateDialog.value = false
    form.value = { name: '', system_name: '', level: null, client_org: '', start_date: '', deadline: '', notes: '' }
    ElMessage.success('项目创建成功')
  } catch {
    ElMessage.error('创建失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => projectsStore.fetchProjects())
</script>

<style scoped>
.kanban-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
  overflow: hidden;
  padding-top: 56px;
}

.kanban-main {
  flex: 1;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 16px;
}

.kanban-board {
  display: flex;
  gap: 12px;
  height: 100%;
  min-width: 900px;
}

.kanban-column {
  flex: 1;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  background: #f7f8fa;
  border-radius: 10px;
  overflow: hidden;
}

.column-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-top: 3px solid transparent;
  font-weight: 600;
  font-size: 13px;
  color: #303133;
  flex-shrink: 0;
}

.phase-icon {
  font-size: 15px;
}

.phase-label {
  flex: 1;
}

.phase-count {
  margin-left: auto;
}

.column-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 60px;
}

.empty-placeholder {
  text-align: center;
  color: #c0c4cc;
  font-size: 12px;
  padding: 24px 0;
}

.card-ghost {
  opacity: 0.4;
}
</style>
