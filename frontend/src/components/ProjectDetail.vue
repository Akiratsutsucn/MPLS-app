<template>
  <el-drawer v-model="visible" :title="project?.name || '项目详情'" size="600px" @close="emit('close')">
    <template v-if="project">
      <!-- Basic Info -->
      <el-descriptions :column="2" border size="small" class="section">
        <el-descriptions-item label="系统名称">{{ project.system_name }}</el-descriptions-item>
        <el-descriptions-item label="等保等级">{{ LEVELS[project.level] }}</el-descriptions-item>
        <el-descriptions-item label="当前阶段">
          <el-tag :color="PHASE_MAP[project.phase]?.bgColor" :style="{ color: PHASE_MAP[project.phase]?.color }" size="small">
            {{ PHASE_MAP[project.phase]?.icon }} {{ PHASE_MAP[project.phase]?.label }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="负责人">{{ project.assignee_name || '—' }}</el-descriptions-item>
        <el-descriptions-item label="客户单位">{{ project.client_org || '—' }}</el-descriptions-item>
        <el-descriptions-item label="截止日期">{{ project.deadline ? new Date(project.deadline).toLocaleDateString('zh-CN') : '—' }}</el-descriptions-item>
      </el-descriptions>

      <!-- Tabs -->
      <el-tabs v-model="activeTab" class="detail-tabs">
        <!-- Checklist Tab -->
        <el-tab-pane label="检查清单" name="checklist">
          <div v-for="phase in PHASES" :key="phase.key" class="checklist-phase">
            <div class="phase-title" :style="{ color: phase.color }">
              {{ phase.icon }} {{ phase.label }}
              <span class="phase-progress">{{ phaseProgress(phase.key) }}</span>
            </div>
            <div v-for="item in phaseItems(phase.key)" :key="item.id" class="checklist-item">
              <el-checkbox
                :model-value="item.is_completed"
                @change="(val) => toggleItem(item, val)"
              >
                <span :class="{ completed: item.is_completed }">{{ item.content }}</span>
              </el-checkbox>
              <el-button v-if="item.is_custom" type="danger" link size="small" @click="deleteCheckItem(item)">删除</el-button>
            </div>
            <div class="add-item" v-if="project.phase === phase.key">
              <el-input
                v-model="newCheckItem[phase.key]"
                size="small"
                placeholder="添加检查项..."
                @keyup.enter="addCheckItem(phase.key)"
              >
                <template #append>
                  <el-button @click="addCheckItem(phase.key)">添加</el-button>
                </template>
              </el-input>
            </div>
          </div>
        </el-tab-pane>

        <!-- Documents Tab -->
        <el-tab-pane label="文档" name="documents">
          <el-upload
            :action="`/api/projects/${projectId}/documents`"
            :headers="uploadHeaders"
            :on-success="onUploadSuccess"
            :on-error="() => ElMessage.error('上传失败')"
            :before-upload="beforeUpload"
            drag
            class="doc-upload"
          >
            <el-icon class="el-icon--upload"><Upload /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
            <template #tip><div class="el-upload__tip">单文件不超过 50MB</div></template>
          </el-upload>
          <el-table :data="documents" size="small" style="margin-top: 12px">
            <el-table-column prop="filename" label="文件名" min-width="180" />
            <el-table-column prop="phase" label="阶段" width="100">
              <template #default="{ row }">{{ PHASE_MAP[row.phase]?.label }}</template>
            </el-table-column>
            <el-table-column label="大小" width="80">
              <template #default="{ row }">{{ formatSize(row.filesize) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link size="small" @click="downloadDoc(row)">下载</el-button>
                <el-button link type="danger" size="small" @click="deleteDoc(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Logs Tab -->
        <el-tab-pane label="日志" name="logs">
          <div class="log-input">
            <el-input v-model="newLog" placeholder="添加备忘录..." :rows="2" type="textarea" />
            <el-button type="primary" size="small" style="margin-top: 8px" @click="addLog" :disabled="!newLog.trim()">添加</el-button>
          </div>
          <el-timeline class="log-timeline">
            <el-timeline-item
              v-for="log in logs"
              :key="log.id"
              :timestamp="new Date(log.created_at).toLocaleString('zh-CN')"
              :type="log.log_type === 'system' ? 'primary' : 'success'"
              placement="top"
            >
              <div class="log-content">
                <el-tag v-if="log.log_type === 'system'" size="small" type="info">系统</el-tag>
                <span>{{ log.content }}</span>
              </div>
              <div v-if="log.author_name" class="log-author">{{ log.author_name }}</div>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>

        <!-- Reminders Tab -->
        <el-tab-pane label="提醒" name="reminders">
          <div class="reminder-form">
            <el-input v-model="newReminder.title" placeholder="提醒标题" size="small" style="flex: 1" />
            <el-date-picker v-model="newReminder.remind_date" type="date" placeholder="日期" size="small" value-format="YYYY-MM-DD" style="width: 160px" />
            <el-button type="primary" size="small" @click="addReminder" :disabled="!newReminder.title || !newReminder.remind_date">添加</el-button>
          </div>
          <el-table :data="reminders" size="small" style="margin-top: 12px">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="remind_date" label="提醒日期" width="120" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="isOverdue(row.remind_date) ? 'danger' : 'success'" size="small">
                  {{ isOverdue(row.remind_date) ? '已到期' : '待提醒' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button link type="danger" size="small" @click="deleteReminder(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <!-- Export button -->
      <div class="export-bar">
        <el-button type="primary" @click="exportReport" :loading="exporting">导出 Word 报告</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { PHASES, LEVELS, PHASE_MAP } from '../utils/constants.js'
import * as checklistApi from '../api/checklist.js'
import * as documentsApi from '../api/documents.js'
import * as logsApi from '../api/logs.js'
import * as remindersApi from '../api/reminders.js'
import { exportReport as exportApi } from '../api/export.js'
import { getProject } from '../api/projects.js'

const props = defineProps({ projectId: { type: Number, required: true } })
const emit = defineEmits(['close', 'updated'])

const visible = ref(true)
const project = ref(null)
const activeTab = ref('checklist')
const checklist = ref([])
const documents = ref([])
const logs = ref([])
const reminders = ref([])
const newLog = ref('')
const newCheckItem = ref({})
const newReminder = ref({ title: '', remind_date: '' })
const exporting = ref(false)

const uploadHeaders = { Authorization: `Bearer ${localStorage.getItem('token')}` }

function phaseItems(phaseKey) {
  return checklist.value.filter(i => i.phase === phaseKey).sort((a, b) => a.sort_order - b.sort_order)
}

function phaseProgress(phaseKey) {
  const items = phaseItems(phaseKey)
  if (!items.length) return ''
  const done = items.filter(i => i.is_completed).length
  return `${done}/${items.length}`
}

async function loadData() {
  const [projRes, clRes, docRes, logRes, remRes] = await Promise.all([
    getProject(props.projectId),
    checklistApi.getChecklist(props.projectId),
    documentsApi.getDocuments(props.projectId),
    logsApi.getLogs(props.projectId),
    remindersApi.getReminders(props.projectId),
  ])
  project.value = projRes.data
  checklist.value = clRes.data
  documents.value = docRes.data
  logs.value = logRes.data
  reminders.value = remRes.data
}

async function toggleItem(item, val) {
  await checklistApi.toggleItem(props.projectId, item.id, { is_completed: val })
  item.is_completed = val
  emit('updated')
}

async function addCheckItem(phase) {
  const content = newCheckItem.value[phase]?.trim()
  if (!content) return
  const res = await checklistApi.addItem(props.projectId, { content, phase })
  checklist.value.push(res.data)
  newCheckItem.value[phase] = ''
}

async function deleteCheckItem(item) {
  await checklistApi.deleteItem(props.projectId, item.id)
  checklist.value = checklist.value.filter(i => i.id !== item.id)
}

function onUploadSuccess(res) {
  documents.value.push(res)
  ElMessage.success('上传成功')
}

function beforeUpload(file) {
  if (file.size > 50 * 1024 * 1024) { ElMessage.error('文件不能超过 50MB'); return false }
  return true
}

function downloadDoc(doc) { documentsApi.downloadDocument(props.projectId, doc.id) }

async function deleteDoc(doc) {
  await documentsApi.deleteDocument(props.projectId, doc.id)
  documents.value = documents.value.filter(d => d.id !== doc.id)
  ElMessage.success('已删除')
}

async function addLog() {
  if (!newLog.value.trim()) return
  const res = await logsApi.addLog(props.projectId, newLog.value.trim())
  logs.value.unshift(res.data)
  newLog.value = ''
}

async function addReminder() {
  const res = await remindersApi.addReminder(props.projectId, newReminder.value)
  reminders.value.push(res.data)
  newReminder.value = { title: '', remind_date: '' }
  ElMessage.success('提醒已添加')
}

async function deleteReminder(rem) {
  await remindersApi.deleteReminder(props.projectId, rem.id)
  reminders.value = reminders.value.filter(r => r.id !== rem.id)
}

async function exportReport() {
  exporting.value = true
  try { await exportApi(props.projectId) } catch { ElMessage.error('导出失败') } finally { exporting.value = false }
}

function formatSize(bytes) {
  if (!bytes) return '—'
  if (bytes < 1024) return bytes + 'B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + 'KB'
  return (bytes / 1048576).toFixed(1) + 'MB'
}

function isOverdue(date) { return new Date(date) <= new Date() }

onMounted(loadData)
</script>

<style scoped>
.section { margin-bottom: 16px; }
.detail-tabs { margin-top: 16px; }
.checklist-phase { margin-bottom: 16px; }
.phase-title { font-weight: 600; font-size: 14px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.phase-progress { font-size: 12px; color: #909399; font-weight: normal; }
.checklist-item { display: flex; align-items: center; justify-content: space-between; padding: 4px 0; }
.completed { text-decoration: line-through; color: #c0c4cc; }
.add-item { margin-top: 8px; }
.doc-upload { margin-bottom: 8px; }
.log-input { margin-bottom: 16px; }
.log-timeline { margin-top: 16px; }
.log-content { display: flex; align-items: center; gap: 6px; }
.log-author { font-size: 12px; color: #909399; margin-top: 2px; }
.reminder-form { display: flex; gap: 8px; align-items: center; }
.export-bar { margin-top: 24px; padding-top: 16px; border-top: 1px solid #eee; text-align: center; }
</style>
