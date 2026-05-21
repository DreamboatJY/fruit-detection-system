<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">个人中心</h1>
      <p class="page-subtitle">管理您的账户信息</p>
    </div>

    <div class="profile-content">
      <div class="avatar-section">
        <el-avatar :size="100" :src="userInfo.avatar" />
        <div class="avatar-actions">
          <el-button type="primary" plain size="small">更换头像</el-button>
        </div>
      </div>

      <el-form :model="userInfo" label-width="100px" class="info-form">
        <el-form-item label="用户名">
          <el-input v-model="userInfo.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="userInfo.email" />
        </el-form-item>
        <el-form-item label="注册时间">
          <el-input v-model="userInfo.regTime" disabled />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveProfile">保存修改</el-button>
        </el-form-item>
      </el-form>

      <div class="stats-section">
        <h3>使用统计</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ stats.totalDetections }}</div>
            <div class="stat-label">总检测次数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.totalTargets }}</div>
            <div class="stat-label">累计检测目标</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.successRate }}%</div>
            <div class="stat-label">检测成功率</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from "vue";
import { ElMessage } from "element-plus";

const userInfo = reactive({
  username: "demo_user",
  email: "demo@example.com",
  avatar: "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
  regTime: "2024-01-01",
});

const stats = reactive({
  totalDetections: 128,
  totalTargets: 892,
  successRate: 98.5,
});

const saveProfile = () => {
  ElMessage.success("保存成功");
};
</script>

<style scoped>
.profile-page {
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

.profile-content {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-section {
  text-align: center;
  padding-bottom: 30px;
  border-bottom: 1px solid #eee;
  margin-bottom: 30px;
}

.avatar-actions {
  margin-top: 16px;
}

.info-form {
  max-width: 500px;
  margin-bottom: 30px;
}

.stats-section h3 {
  margin-bottom: 20px;
  font-size: 18px;
}

.stats-grid {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 150px;
  background: #f5f5f5;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #27ae60;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}
</style>