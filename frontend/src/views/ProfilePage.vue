<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">个人中心</h1>
      <p class="page-subtitle">管理你的账户信息和使用统计</p>
    </div>

    <div class="profile-content">
      <div class="user-info-card">
        <div class="user-avatar-section">
          <el-avatar class="profile-avatar" :size="80">
            <img v-if="user?.avatar_url" :src="user.avatar_url" alt="用户头像" />
            <span v-else>{{ avatarText }}</span>
          </el-avatar>

          <div class="user-basic-info">
            <div class="user-name">{{ displayName }}</div>
            <div class="user-meta">{{ user?.email || "未设置邮箱" }}</div>
            <div class="user-role">{{ roleText }}</div>
            <div class="user-actions">
              <el-button size="small" type="primary" plain @click="openProfileDialog">
                编辑资料
              </el-button>
              <el-upload
                action=""
                :show-file-list="false"
                :http-request="handleAvatarUpload"
                :before-upload="beforeAvatarUpload"
              >
                <el-button size="small" plain :loading="avatarUploading">上传头像</el-button>
              </el-upload>
              <el-button size="small" plain @click="openPasswordDialog">修改密码</el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="stats-cards" v-loading="statsLoading">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_detections }}</div>
          <div class="stat-label">总检测次数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_targets }}</div>
          <div class="stat-label">累计检测目标</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.success_rate }}%</div>
          <div class="stat-label">检测成功率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.usage_days }}</div>
          <div class="stat-label">使用天数</div>
        </div>
      </div>
    </div>

    <el-dialog v-model="profileDialogVisible" title="编辑资料" width="420px">
      <el-form ref="profileFormRef" :model="profileForm" :rules="profileRules" label-width="80px">
        <el-form-item label="用户名">
          <el-input :model-value="user?.username" disabled />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="profileForm.nickname" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="profileDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="profileSaving" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="420px">
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="90px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordSaving" @click="savePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { changePassword, getUserStats } from "../api/auth";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();

const profileDialogVisible = ref(false);
const passwordDialogVisible = ref(false);
const profileSaving = ref(false);
const passwordSaving = ref(false);
const avatarUploading = ref(false);
const statsLoading = ref(false);
const profileFormRef = ref(null);
const passwordFormRef = ref(null);

const stats = reactive({
  total_detections: 0,
  total_targets: 0,
  success_rate: 0,
  usage_days: 0,
});

const profileForm = reactive({
  nickname: "",
  email: "",
});

const passwordForm = reactive({
  old_password: "",
  new_password: "",
  confirm_password: "",
});

const user = computed(() => authStore.user);
const displayName = computed(() => authStore.displayName);
const roleText = computed(() => (user.value?.role === "admin" ? "管理员" : "普通用户"));
const avatarText = computed(() => (displayName.value || "用").slice(0, 1).toUpperCase());

const profileRules = {
  nickname: [{ max: 50, message: "昵称不能超过 50 个字符", trigger: "blur" }],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
};

const validateConfirmPassword = (_rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error("两次输入的密码不一致"));
    return;
  }
  callback();
};

const passwordRules = {
  old_password: [{ required: true, min: 6, message: "请输入至少 6 位旧密码", trigger: "blur" }],
  new_password: [{ required: true, min: 6, message: "请输入至少 6 位新密码", trigger: "blur" }],
  confirm_password: [
    { required: true, message: "请再次输入新密码", trigger: "blur" },
    { validator: validateConfirmPassword, trigger: "blur" },
  ],
};

const loadStats = async () => {
  statsLoading.value = true;
  try {
    const response = await getUserStats();
    Object.assign(stats, response.data || {});
  } catch (error) {
    console.error("获取用户统计失败:", error);
  } finally {
    statsLoading.value = false;
  }
};

const openProfileDialog = () => {
  profileForm.nickname = user.value?.nickname || "";
  profileForm.email = user.value?.email || "";
  profileDialogVisible.value = true;
};

const saveProfile = async () => {
  await profileFormRef.value?.validate();
  profileSaving.value = true;
  try {
    await authStore.updateProfile({
      nickname: profileForm.nickname,
      email: profileForm.email,
    });
    profileDialogVisible.value = false;
    ElMessage.success("资料更新成功");
  } finally {
    profileSaving.value = false;
  }
};

const openPasswordDialog = () => {
  Object.assign(passwordForm, {
    old_password: "",
    new_password: "",
    confirm_password: "",
  });
  passwordDialogVisible.value = true;
};

const savePassword = async () => {
  await passwordFormRef.value?.validate();
  passwordSaving.value = true;
  try {
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    });
    passwordDialogVisible.value = false;
    ElMessage.success("密码修改成功");
  } finally {
    passwordSaving.value = false;
  }
};

const beforeAvatarUpload = (file) => {
  const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
  if (!allowedTypes.includes(file.type)) {
    ElMessage.warning("头像仅支持 jpg、jpeg、png、webp 格式");
    return false;
  }
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning("头像文件不能超过 2MB");
    return false;
  }
  return true;
};

const handleAvatarUpload = async ({ file }) => {
  avatarUploading.value = true;
  try {
    await authStore.uploadUserAvatar(file);
    ElMessage.success("头像上传成功");
  } finally {
    avatarUploading.value = false;
  }
};

onMounted(async () => {
  if (!authStore.user) {
    await authStore.fetchCurrentUser().catch(() => {});
  }
  loadStats();
});
</script>

<style scoped>
.profile-page {
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

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.user-info-card {
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--border-light);
}

.user-avatar-section {
  display: flex;
  align-items: center;
}

.profile-avatar {
  flex: 0 0 auto;
  font-size: 28px;
  font-weight: 600;
  background: var(--primary-gradient);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
}

.user-basic-info {
  margin-left: 24px;
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.user-meta,
.user-role {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.user-actions {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.stat-card {
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  padding: 24px;
  text-align: center;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--border-light);
  transition: all var(--transition-fast);
}

.stat-card:hover {
  box-shadow: var(--card-shadow-hover);
  transform: translateY(-2px);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

@media (max-width: 900px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .user-avatar-section {
    align-items: flex-start;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
