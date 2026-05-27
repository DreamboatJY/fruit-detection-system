<template>
  <div class="login-container">
    <div class="login-background">
      <div class="bg-shape bg-shape-1"></div>
      <div class="bg-shape bg-shape-2"></div>
      <div class="bg-shape bg-shape-3"></div>
    </div>

    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="36" color="#ffffff"><Picture /></el-icon>
        </div>
        <h1 class="login-title">钢材表面缺陷智能检测平台</h1>
        <p class="login-subtitle">NEU-DET 数据集 · 六类缺陷精准识别</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item class="form-actions">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <router-link to="/forgot-password" class="forgot-password">忘记密码?</router-link>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="isSubmitting"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-link">
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { Picture, User, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const isSubmitting = ref(false);

const loginForm = reactive({
  username: "",
  password: "",
  remember: false,
});

const loginRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度在3到20个字符", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度在6到30个字符", trigger: "blur" },
  ],
};

const loginFormRef = ref(null);

const handleLogin = async () => {
  if (!loginFormRef.value) return;

  const valid = await loginFormRef.value.validate().catch(() => false);
  if (!valid) return;

  try {
    isSubmitting.value = true;
    await authStore.login({
      username: loginForm.username,
      password: loginForm.password,
    });
    ElMessage.success("登录成功");
    router.push("/detection");
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  position: relative;
  overflow: hidden;
}

.login-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}

.bg-shape-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  top: -150px;
  right: -100px;
  animation: float 8s ease-in-out infinite;
}

.bg-shape-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #10b981, #3b82f6);
  bottom: -100px;
  left: -80px;
  animation: float 10s ease-in-out infinite reverse;
}

.bg-shape-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #8b5cf6, #ec4899);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: float 12s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-30px) scale(1.05); }
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-xl);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
  animation: slideUp 0.5s ease-out;
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  background: var(--primary-gradient);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
}

.login-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.login-subtitle {
  font-size: 13px;
  color: #64748b;
  letter-spacing: 0.02em;
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: var(--radius-md);
  padding: 12px 16px;
  box-shadow: 0 0 0 1px #e2e8f0;
  transition: all var(--transition-fast);
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cbd5e1;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--primary-color);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.form-actions :deep(.el-checkbox__label) {
  font-size: 13px;
  color: #64748b;
}

.forgot-password {
  font-size: 13px;
  color: var(--primary-color);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.forgot-password:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  height: 48px;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.1em;
  background: var(--primary-gradient);
  border: none;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transition: all var(--transition-fast);
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.register-link {
  text-align: center;
  font-size: 13px;
  color: #64748b;
}

.register-link a {
  color: var(--primary-color);
  margin-left: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.register-link a:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-card {
    margin: 16px;
    padding: 36px 24px;
  }

  .login-title {
    font-size: 20px;
  }
}
</style>
