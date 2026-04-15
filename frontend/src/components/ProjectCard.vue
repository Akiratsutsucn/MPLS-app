<template>
  <div class="project-card" @click="emit('click', project)">
    <div class="card-border" :style="{ backgroundColor: phaseColor }"></div>
    <div class="card-body">
      <div class="card-header">
        <span class="project-name">{{ project.name }}</span>
        <el-tag v-if="urgencyTag" :type="urgencyTag.type" size="small" class="urgency-tag">
          {{ urgencyTag.text }}
        </el-tag>
      </div>
      <div class="card-meta">
        <span class="meta-item">
          <el-tag size="small" :color="levelColor" effect="plain">{{ levelLabel }}</el-tag>
        </span>
        <span class="meta-item meta-text">👤 {{ project.owner_name || project.owner || '—' }}</span>
      </div>
      <div class="card-meta">
        <span class="meta-text">📅 {{ formatDate(project.deadline) }}</span>
      </div>
      <div v-if="project.checklist_total > 0" class="card-progress">
        <el-progress
          :percentage="progressPercent"
          :stroke-width="4"
          :show-text="false"
          :color="phaseColor"
        />
        <span class="progress-text">{{ project.checklist_done || 0 }}/{{ project.checklist_total }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { PHASES, LEVELS } from '../utils/constants.js'

const props = defineProps({
  project: { type: Object, required: true },
})
const emit = defineEmits(['click'])

const phaseColor = computed(() => {
  const phase = PHASES.find((p) => p.key === props.project.phase)
  return phase?.color || '#909399'
})

const levelLabel = computed(() => LEVELS[props.project.level] || `${props.project.level}级`)

const levelColor = computed(() => {
  const colors = { 1: '#e9e9eb', 2: '#d9ecff', 3: '#fdf6ec', 4: '#fef0f0', 5: '#f0f9eb' }
  return colors[props.project.level] || '#e9e9eb'
})

const progressPercent = computed(() => {
  const total = props.project.checklist_total || 0
  const done = props.project.checklist_done || 0
  return total > 0 ? Math.round((done / total) * 100) : 0
})

const urgencyTag = computed(() => {
  if (!props.project.deadline) return null
  const days = Math.ceil((new Date(props.project.deadline) - Date.now()) / 86400000)
  if (days < 0) return { type: 'danger', text: '已逾期' }
  if (days <= 3) return { type: 'danger', text: `${days}天` }
  if (days <= 7) return { type: 'warning', text: `${days}天` }
  return null
})

function formatDate(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}
</script>

<style scoped>
.project-card {
  display: flex;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
  overflow: hidden;
}

.project-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.14);
  transform: translateY(-1px);
}

.card-border {
  width: 4px;
  flex-shrink: 0;
}

.card-body {
  flex: 1;
  padding: 10px 12px;
  min-width: 0;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 6px;
  margin-bottom: 6px;
}

.project-name {
  font-weight: 600;
  font-size: 13px;
  color: #303133;
  line-height: 1.4;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.urgency-tag {
  flex-shrink: 0;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.meta-text {
  font-size: 12px;
  color: #909399;
}

.card-progress {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
}

.card-progress .el-progress {
  flex: 1;
}

.progress-text {
  font-size: 11px;
  color: #909399;
  white-space: nowrap;
}
</style>
