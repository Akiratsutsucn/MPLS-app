<template>
  <div class="list-page">
    <NavBar @create="showCreateDialog = true" @search="handleSearch" />

    <main class="list-main">
      <!-- Filters -->
      <div class="filter-bar">
        <el-select v-model="filterPhase" placeholder="阶段筛选" clearable style="width: 140px">
          <el-option v-for="p in PHASES" :key="p.key" :label="p.label" :value="p.key" />
        </el-select>
        <el-select v-model="filterLevel" placeholder="等级筛选" clearable style="width: 120px">
          <el-option v-for="(label, val) in LEVELS" :key="val" :label="label" :value="Number(val)" />
        </el-select>
      </div>

      <!-- Table -->
      <el-table
        :data="filteredProjects"
        stripe
        style="width: 100%"
        @row-click="openDetail"
        :default-sort="{ prop: 'deadline', order: 'ascending' }"
      >
        <el-table-column prop="name" label="项目名称" min-width="160" />
        <el-table-column prop="system_name" label="系统名称" min-width="140" />
        <el-table-column prop="level" label="等保等级" width="100" sortable>
          <template #default="{ row }">
            <el-tag size="small">{{ LEVELS[row.level] || row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phase" label="当前阶段" width="120" sortable>
          <template #default="{ row }">
            <el-tag :color="PHASE_MAP[row.phase]?.bgColor" :style="{ color: PHASE_MAP[row.phase]?.color, borderColor: PHASE_MAP[row.phase]?.color }" size="small">
              {{ PHASE_MAP[row.phase]?.icon }} {{ PHASE_MAP[row.phase]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee_name" label="负责人" width="100" />
        <el-table-column prop="client_org" label="客户单位" min-width="120" />
        <el-table-column prop="deadline" label="截止日期" width="120" sortable>
          <template #default="{ row }">
            <span :class="{ 'text-danger': isUrgent(row.deadline) }">
              {{ formatDate(row.deadline) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="完成度" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.checklist_completion || 0" :stroke-width="6" :show-text="true" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link size="small" @click.stop="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </main>

    <!-- Reuse create dialog from KanbanView pattern -->
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
        <el-form-item label="截止日期">
          <el-date-picker v-model="form.deadline" type="date" placeholder="请选择" style="width: 100%" value-format="YYYY-MM-DD" />
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import NavBar from '../components/NavBar.vue'
import ProjectDetail from '../components/ProjectDetail.vue'
import { PHASES, LEVELS, PHASE_MAP } from '../utils/constants.js'
import { useProjectsStore } from '../stores/projects.js'

const projectsStore = useProjectsStore()

const searchQuery = ref('')
const filterPhase = ref('')
const filterLevel = ref('')
const showCreateDialog = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const detailProject = ref(null)

const form = ref({ name: '', system_name: '', level: null, client_org: '', deadline: '', notes: '' })
const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  system_name: [{ required: true, message: '请输入系统名称', trigger: 'blur' }],
  level: [{ required: true, message: '请选择等保等级', trigger: 'change' }],
}

const filteredProjects = computed(() => {
  let list = projectsStore.projects
  const q = searchQuery.value.trim().toLowerCase()
  if (q) list = list.filter(p => p.name?.toLowerCase().includes(q) || p.system_name?.toLowerCase().includes(q))
  if (filterPhase.value) list = list.filter(p => p.phase === filterPhase.value)
  if (filterLevel.value) list = list.filter(p => p.level === filterLevel.value)
  return list
})

function handleSearch(q) { searchQuery.value = q }

function openDetail(row) { detailProject.value = row }

function onProjectUpdated() { projectsStore.fetchProjects() }

function isUrgent(deadline) {
  if (!deadline) return false
  return Math.ceil((new Date(deadline) - Date.now()) / 86400000) <= 3
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('zh-CN')
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除项目「${row.name}」？`, '确认删除', { type: 'warning' })
  await projectsStore.deleteProject(row.id)
  ElMessage.success('已删除')
}

async function submitCreate() {
  await formRef.value.validate()
  submitting.value = true
  try {
    await projectsStore.createProject({ ...form.value })
    showCreateDialog.value = false
    form.value = { name: '', system_name: '', level: null, client_org: '', deadline: '', notes: '' }
    ElMessage.success('项目创建成功')
  } catch { ElMessage.error('创建失败') } finally { submitting.value = false }
}

onMounted(() => projectsStore.fetchProjects())
</script>

<style scoped>
.list-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
  padding-top: 56px;
}
.list-main {
  flex: 1;
  padding: 16px;
  overflow: auto;
}
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.text-danger { color: #F56C6C; font-weight: 600; }
</style>
