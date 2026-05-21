<template>
  <div class="history-page">
    <div class="page-header">
      <h1 class="page-title">历史记录</h1>
      <p class="page-subtitle">查看所有检测历史</p>
    </div>

    <div class="history-list">
      <div v-for="item in historyList" :key="item.id" class="history-item">
        <div class="history-image">
          <img :src="item.image" alt="检测图片" />
        </div>
        <div class="history-info">
          <div class="history-name">{{ item.name }}</div>
          <div class="history-time">{{ item.time }}</div>
          <div class="history-targets">
            <el-tag v-for="tag in item.targets" :key="tag" size="small">
              {{ tag }}
            </el-tag>
          </div>
        </div>
        <div class="history-actions">
          <el-button type="primary" link @click="viewDetail(item)">查看详情</el-button>
          <el-button type="danger" link @click="deleteRecord(item)">删除</el-button>
        </div>
      </div>

      <div v-if="historyList.length === 0" class="empty-state">
        <p>暂无检测记录</p>
        <el-button type="primary" @click="goToDetection">开始检测</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const historyList = ref([
  {
    id: 1,
    name: "机场航拍图",
    image: "https://picsum.photos/200/150?random=1",
    time: "2024-01-15 14:30",
    targets: ["飞机", "油罐"],
  },
  {
    id: 2,
    name: "港口卫星图",
    image: "https://picsum.photos/200/150?random=2",
    time: "2024-01-14 10:20",
    targets: ["船舶", "集装箱"],
  },
]);

const viewDetail = (item) => {
  console.log("查看详情:", item);
};

const deleteRecord = (item) => {
  const index = historyList.value.findIndex((i) => i.id === item.id);
  if (index > -1) {
    historyList.value.splice(index, 1);
  }
};

const goToDetection = () => {
  router.push("/detection");
};
</script>

<style scoped>
.history-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #666;
}

.history-list {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.history-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  gap: 20px;
}

.history-item:last-child {
  border-bottom: none;
}

.history-image img {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.history-info {
  flex: 1;
}

.history-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.history-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.history-targets {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.history-actions {
  display: flex;
  gap: 12px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #999;
}
</style>