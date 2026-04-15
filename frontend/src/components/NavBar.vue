<template>
  <header class="navbar">
    <!-- 左侧：Logo + 标题 -->
    <div class="navbar-left">
      <el-icon class="navbar-logo" :size="24" color="#409eff">
        <Grid />
      </el-icon>
      <span class="navbar-title">等保项目管理</span>
    </div>

    <!-- 中间：视图切换 -->
    <div class="navbar-center">
      <el-radio-group :model-value="currentView" @change="handleViewChange">
        <el-radio-button value="/">
          <el-icon><Grid /></el-icon>
          看板
        </el-radio-button>
        <el-radio-button value="/list">
          <el-icon><List /></el-icon>
          列表
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 右侧：操作区 -->
    <div class="navbar-right">
      <!-- 搜索框（小屏隐藏） -->
      <el-input
        v-model="searchQuery"
        placeholder="搜索项目..."
        prefix-icon="Search"
        clearable
        class="navbar-search"
        @input="handleSearch"
        @clear="handleSearch"
      />

      <!-- 新建项目 -->
      <el-button type="primary" @click="emit('create')">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>

      <!-- 即将到期提醒 -->
      <el-badge :value="upcomingCount || 0" :hidden="!upcomingCount" type="danger">
        <el-button :icon="Bell" circle title="即将到期提醒" @click="handleBellClick" />
      </el-badge>

      <!-- 用户下拉菜单 -->
      <el-dropdown trigger="click" @command="handleCommand">
        <span class="navbar-user">
          <el-avatar :size="28" class="user-avatar">
            {{ userInitial }}
          </el-avatar>
          <span class="user-name">{{ authStore.user?.name || authStore.user?.username }}</span>
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Grid, List, Plus, Bell, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth.js'
import { getUpcoming } from '../api/dashboard.js'

const emit = defineEmits(['create', 'search'])

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const searchQuery = ref('')
const upcomingCount = ref(0)

const currentView = computed(() => route.path)

const userInitial = computed(() => {
  const name = authStore.user?.name || authStore.user?.username || ''
  return name.charAt(0).toUpperCase()
})

function handleViewChange(path) {
  router.push(path)
}

function handleSearch() {
  emit('search', searchQuery.value)
}

function handleBellClick() {
  router.push('/list')
}

async function handleCommand(command) {
  if (command === 'logout') {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning',
    }).catch(() => null)

    authStore.logout()
    router.push('/login')
  }
}

onMounted(async () => {
  try {
    const res = await getUpcoming()
    upcomingCount.value = res.data?.length ?? 0
  } catch {
    // 静默失败，不影响导航栏渲染
  }
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  gap: 16px;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.navbar-logo {
  flex-shrink: 0;
}

.navbar-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
}

.navbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.navbar-search {
  width: 200px;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #303133;
  font-size: 14px;
}

.user-avatar {
  background-color: #409eff;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-name {
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 小屏隐藏搜索框 */
@media (max-width: 768px) {
  .navbar-search {
    display: none;
  }
}
</style>
