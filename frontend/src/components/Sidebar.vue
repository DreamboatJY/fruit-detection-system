<template>
  <div class="sidebar-container">
    <div class="logo-section">
      <div class="logo-icon">
        <Monitor style="color: white; font-size: 20px" />
      </div>
      <div class="logo-text">
        <div class="logo-title">钢材表面缺陷检测平台</div>
        <div class="logo-subtitle">六类缺陷·精准识别</div>
      </div>
    </div>

    <div class="nav-menu">
      <div
        v-for="item in menuList"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentPath === item.path }"
        @click="handleMenuClick(item)"
      >
        <el-icon :size="18" class="nav-icon"><component :is="item.icon" /></el-icon>
        <span class="nav-text">{{ item.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  Monitor,
  Picture,
  Clock,
  ChatDotRound,
  DataLine,
  User,
} from "@element-plus/icons-vue";

const router = useRouter();
const route = useRoute();

const menuList = [
  {
    name: "智能检测",
    icon: Picture,
    path: "/detection",
  },
  {
    name: "历史记录",
    icon: Clock,
    path: "/history",
  },
  {
    name: "AI 问答",
    icon: ChatDotRound,
    path: "/qa",
  },
  {
    name: "目标库",
    icon: DataLine,
    path: "/targets",
  },
  {
    name: "个人中心",
    icon: User,
    path: "/profile",
  },
];

const currentPath = computed(() => route.path);

const handleMenuClick = (item) => {
  router.push(item.path);
};
</script>

<style scoped>
.sidebar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo-section {
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.logo-text {
  overflow: hidden;
}

.logo-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
  white-space: nowrap;
  letter-spacing: -0.01em;
}

.logo-subtitle {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 2px;
  line-height: 1.3;
  white-space: nowrap;
  letter-spacing: 0.02em;
}

.nav-menu {
  flex: 1;
  padding: 20px 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  flex-direction: row;
  padding: 14px 14px;
  border-radius: var(--radius-md);
  margin-bottom: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-gradient);
  border-radius: 0 2px 2px 0;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.nav-item:hover {
  background-color: var(--primary-light);
}

.nav-item:hover::before {
  opacity: 0.5;
}

.nav-item.active {
  background: linear-gradient(135deg, var(--primary-light) 0%, rgba(59, 130, 246, 0.08) 100%);
  color: var(--primary-color);
  font-weight: 600;
}

.nav-item.active::before {
  opacity: 1;
}

.nav-item.active .nav-icon {
  color: var(--primary-color);
}

.nav-icon {
  font-size: 18px;
  margin-right: 12px;
  color: var(--text-secondary);
  flex-shrink: 0;
  transition: color var(--transition-fast);
}

.nav-item:hover .nav-icon {
  color: var(--primary-color);
}

.nav-text {
  font-size: 14px;
  line-height: 1.4;
  transition: color var(--transition-fast);
}
</style>
