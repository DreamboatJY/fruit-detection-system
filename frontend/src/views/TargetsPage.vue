<template>
  <div class="targets-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">目标检测库</h1>
      <p class="page-subtitle">平台支持检测的所有钢材表面缺陷类别</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-container">
      <el-input
        v-model="searchQuery"
        placeholder="搜索目标类别..."
        size="default"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon target-icon">
          <el-icon><Aim /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalTargets }}</div>
          <div class="stat-label">目标总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon category-icon">
          <el-icon><Grid /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ categories.length }}</div>
          <div class="stat-label">类别数量</div>
        </div>
      </div>
    </div>

    <!-- 目标类别列表 -->
    <div class="target-categories">
      <div
        v-for="category in filteredCategories"
        :key="category.id"
        class="category-card"
      >
        <div class="category-header">
          <div
            class="category-icon"
            :style="{ backgroundColor: category.color }"
          >
            <component :is="category.icon" />
          </div>
          <div class="category-info">
            <div class="category-name">{{ category.name }}</div>
            <div class="category-count">
              {{ category.targets.length }} 个目标
            </div>
          </div>
        </div>
        <div class="target-list">
          <div
            v-for="target in category.targets"
            :key="target.id"
            class="target-item"
            @click="showTargetDetail(target)"
          >
            <el-icon :size="14" class="target-item-icon"><CircleCheck /></el-icon>
            <span>{{ target.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredCategories.length === 0" class="empty-state">
      <el-icon :size="64" class="empty-icon"><Help /></el-icon>
      <p class="empty-text">未找到匹配的目标类别</p>
    </div>

    <!-- 目标详情弹窗 -->
    <el-dialog
      v-if="selectedTarget"
      :title="selectedTarget.name"
      :visible.sync="showDialog"
      width="400px"
    >
      <div class="target-detail">
        <div class="detail-icon" :style="{ backgroundColor: getCategoryColor(selectedTarget.categoryId) }">
          <el-icon :size="48"><component :is="getCategoryIcon(selectedTarget.categoryId)" /></el-icon>
        </div>
        <div class="detail-info">
          <div class="detail-item">
            <span class="detail-label">所属类别</span>
            <span class="detail-value">{{ getCategoryName(selectedTarget.categoryId) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">目标描述</span>
            <span class="detail-value">{{ selectedTarget.description }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">检测精度</span>
            <span class="detail-value">{{ selectedTarget.accuracy }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  Search,
  Aim,
  Grid,
  CircleCheck,
  Help,
  WarningFilled,
  CircleCloseFilled,
} from "@element-plus/icons-vue";

const searchQuery = ref("");
const showDialog = ref(false);
const selectedTarget = ref(null);

const categories = ref([
  {
    id: 1,
    name: "裂纹与划痕类",
    icon: WarningFilled,
    color: "#ef4444",
    targets: [
      { id: 1, name: "裂纹", categoryId: 1, description: "钢材表面裂纹缺陷（crazing）", accuracy: "98.5%" },
      { id: 2, name: "划痕", categoryId: 1, description: "钢材表面划痕缺陷（scratches）", accuracy: "97.2%" },
    ],
  },
  {
    id: 2,
    name: "表面杂质类",
    icon: CircleCloseFilled,
    color: "#f59e0b",
    targets: [
      { id: 3, name: "夹杂物", categoryId: 2, description: "钢材表面夹杂物缺陷（inclusion）", accuracy: "96.8%" },
      { id: 4, name: "斑块", categoryId: 2, description: "钢材表面斑块缺陷（patches）", accuracy: "95.6%" },
    ],
  },
  {
    id: 3,
    name: "表面变形类",
    icon: Aim,
    color: "#3b82f6",
    targets: [
      { id: 5, name: "麻面", categoryId: 3, description: "钢材表面麻点缺陷（pitted_surface）", accuracy: "99.1%" },
      { id: 6, name: "轧制氧化皮", categoryId: 3, description: "轧制氧化皮缺陷（rolled-in_scale）", accuracy: "94.3%" },
    ],
  },
]);

const filteredCategories = computed(() => {
  if (!searchQuery.value) {
    return categories.value;
  }
  const query = searchQuery.value.toLowerCase();
  return categories.value.map((category) => ({
    ...category,
    targets: category.targets.filter((target) =>
      target.name.toLowerCase().includes(query)
    ),
  })).filter((category) =>
    category.name.toLowerCase().includes(query) || category.targets.length > 0
  );
});

const totalTargets = computed(() => {
  return categories.value.reduce((sum, category) => sum + category.targets.length, 0);
});

const getCategoryColor = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.color : "#6b7280";
};

const getCategoryIcon = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.icon : Help;
};

const getCategoryName = (categoryId) => {
  const category = categories.value.find((c) => c.id === categoryId);
  return category ? category.name : "未知";
};

const showTargetDetail = (target) => {
  selectedTarget.value = target;
  showDialog.value = true;
};
</script>

<style scoped>
.targets-page {
  width: 100%;
  animation: fadeIn 0.3s ease-out;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.search-container {
  margin-bottom: 24px;
}

.search-input {
  max-width: 300px;
}

.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  max-width: 200px;
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--card-shadow);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all var(--transition-fast);
  border: 1px solid var(--border-light);
}

.stat-card:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.target-icon {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.category-icon {
  background: var(--primary-gradient);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.stat-info .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-info .stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.target-categories {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.category-card {
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--card-shadow);
  transition: all var(--transition-fast);
  border: 1px solid var(--border-light);
}

.category-card:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}

.category-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.category-icon {
  width: 50px;
  height: 50px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  margin-right: 16px;
}

.category-info .category-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.category-info .category-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.target-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.target-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background-color: var(--bg-tertiary);
  border-radius: 20px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.target-item:hover {
  background-color: var(--success-light);
  color: var(--success-color);
}

.target-item-icon {
  color: var(--success-color);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.empty-icon {
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

.empty-text {
  font-size: 15px;
  color: var(--text-secondary);
}

.target-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.detail-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.detail-info {
  width: 100%;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 600;
}
</style>
