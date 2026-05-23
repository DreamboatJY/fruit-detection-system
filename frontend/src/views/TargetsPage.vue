<template>
  <div class="targets-page">
    <div class="page-header">
      <h1 class="page-title">缺陷目标库</h1>
      <p class="page-subtitle">平台支持检测的缺陷类型</p>
    </div>

    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索目标..."
        prefix-icon="Search"
        clearable
        style="width: 300px"
      />
    </div>

    <div class="categories-list">
      <div v-for="category in filteredCategories" :key="category.name" class="category-card">
        <div class="category-header">
          <div class="category-icon" :style="{ background: category.color }">
            <el-icon><component :is="category.icon" /></el-icon>
          </div>
          <div class="category-info">
            <h3>{{ category.name }}</h3>
            <span>{{ category.items.length }} 个目标</span>
          </div>
        </div>
        <div class="target-list">
          <el-tag
            v-for="item in category.items"
            :key="item.name"
            class="target-tag"
            @click="showTargetDetail(item)"
          >
            {{ item.name }}
          </el-tag>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="selectedTarget?.name" width="400px">
      <div v-if="selectedTarget" class="target-detail">
        <p><strong>类别：</strong>{{ selectedTarget.category }}</p>
        <p><strong>描述：</strong>{{ selectedTarget.description }}</p>
        <p><strong>识别精度：</strong>{{ selectedTarget.accuracy }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  Plane,
  Ship,
  OfficeBuilding,
  Sunrise,
  Setting,
} from "@element-plus/icons-vue";

const searchKeyword = ref("");
const dialogVisible = ref(false);
const selectedTarget = ref(null);

const categories = ref([
  {
    name: "交通工具",
    icon: "Plane",
    color: "#3b82f6",
    items: [
      { name: "飞机", category: "交通工具", description: "各类民用和军用飞机", accuracy: "98.5%" },
      { name: "船舶", category: "交通工具", description: "货轮、客轮、军舰等", accuracy: "97.2%" },
      { name: "汽车", category: "交通工具", description: "各类乘用车、商用车", accuracy: "96.8%" },
    ],
  },
  {
    name: "建筑设施",
    icon: "OfficeBuilding",
    color: "#10b981",
    items: [
      { name: "油罐", category: "建筑设施", description: "储油罐、储气罐", accuracy: "99.1%" },
      { name: "立交桥", category: "建筑设施", description: "城市互通立交桥", accuracy: "97.8%" },
      { name: "体育场", category: "建筑设施", description: "各类体育场馆", accuracy: "96.4%" },
    ],
  },
  {
    name: "自然地物",
    icon: "Sunrise",
    color: "#f59e0b",
    items: [
      { name: "湖泊", category: "自然地物", description: "天然或人工湖泊", accuracy: "99.5%" },
      { name: "河流", category: "自然地物", description: "江河溪流", accuracy: "98.9%" },
      { name: "森林", category: "自然地物", description: "成片树林", accuracy: "97.6%" },
    ],
  },
]);

const filteredCategories = computed(() => {
  if (!searchKeyword.value) return categories.value;
  const keyword = searchKeyword.value.toLowerCase();
  return categories.value
    .map(cat => ({
      ...cat,
      items: cat.items.filter(item => item.name.toLowerCase().includes(keyword)),
    }))
    .filter(cat => cat.items.length > 0);
});

const showTargetDetail = (target) => {
  selectedTarget.value = target;
  dialogVisible.value = true;
};
</script>

<style scoped>
.targets-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #666;
}

.search-bar {
  margin-bottom: 24px;
}

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.category-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.category-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  margin-bottom: 16px;
}

.category-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.category-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
}

.category-info span {
  font-size: 12px;
  color: #999;
}

.target-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.target-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.target-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.target-detail p {
  margin: 12px 0;
  line-height: 1.5;
}
</style>