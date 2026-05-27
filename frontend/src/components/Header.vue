<template>
  <div class="header-container">
    <div class="breadcrumbs">
      <el-icon class="breadcrumb-icon"><House /></el-icon>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-text">智能检测</span>
    </div>

    <div class="header-actions">
      <el-tag type="success" effect="light" class="status-tag">
        <el-icon class="el-icon--left"><Check /></el-icon>
        检测完成
      </el-tag>

      <div class="action-icons">
        <el-icon class="action-icon"><Grid /></el-icon>
        <el-icon class="action-icon"><Bell /></el-icon>
        <el-icon class="action-icon"><QuestionFilled /></el-icon>
        <el-dropdown trigger="click" @command="handleCommand">
          <div class="user-dropdown">
            <el-avatar class="user-avatar" size="32">
              <img v-if="authStore.user?.avatar_url" :src="authStore.user.avatar_url" alt="用户头像" />
              <span v-else>{{ avatarText }}</span>
            </el-avatar>
            <div class="user-info">
              <div class="user-name">{{ authStore.displayName }}</div>
              <div class="user-role">{{ roleText }}</div>
            </div>
            <el-icon class="dropdown-icon"><CaretBottom /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import {
  Check,
  Grid,
  Bell,
  QuestionFilled,
  CaretBottom,
  House,
} from "@element-plus/icons-vue";

const router = useRouter()
const authStore = useAuthStore()

const roleText = computed(() => authStore.user?.role === 'admin' ? '管理员' : '普通用户')
const avatarText = computed(() => (authStore.displayName || '用').slice(0, 1).toUpperCase())

onMounted(() => {
  if (authStore.token && !authStore.user) {
    authStore.fetchCurrentUser().catch(() => {})
  }
})

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.clearAuth()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.breadcrumbs {
  display: flex;
  align-items: center;
}

.breadcrumb-icon {
  font-size: 14px;
  color: var(--text-secondary);
}

.breadcrumb-separator {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0 8px;
}

.breadcrumb-text {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
}

.status-tag {
  margin-right: 24px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.action-icons {
  display: flex;
  align-items: center;
}

.action-icon {
  font-size: 18px;
  color: var(--text-secondary);
  margin-right: 20px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-icon:hover {
  color: var(--primary-color);
  transform: scale(1.1);
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.user-dropdown:hover {
  background-color: var(--bg-tertiary);
}

.user-avatar {
  margin-right: 8px;
  border: 2px solid var(--border-color);
}

.user-info {
  margin-right: 6px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  margin-top: 5px;
  color: var(--text-secondary);
}

.dropdown-icon {
  font-size: 12px;
  color: var(--text-tertiary);
}
</style>
