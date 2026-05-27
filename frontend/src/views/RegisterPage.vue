<template>
  <div class="register-container">
    <div class="register-background">
      <div class="bg-shape bg-shape-1"></div>
      <div class="bg-shape bg-shape-2"></div>
      <div class="bg-shape bg-shape-3"></div>
    </div>

    <div class="register-card">
      <div class="register-header">
        <div class="logo-icon">
          <el-icon :size="36" color="#ffffff"><UserFilled /></el-icon>
        </div>
        <h1 class="register-title">创建账号</h1>
        <p class="register-subtitle">加入我们，开始智能检测之旅</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
            size="large"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            placeholder="请输入邮箱"
            size="large"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
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

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            size="large"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="agree" class="agree-terms">
          <el-checkbox v-model="registerForm.agree" />
          <span>我已阅读并同意</span>
          <a href="#" class="terms-link">《服务条款》</a>
          <span>和</span>
          <a href="#" class="terms-link">《隐私政策》</a>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="register-btn"
            :loading="isSubmitting"
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-link">
        <span>已有账号？</span>
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { UserFilled, User, Message, Lock } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const isSubmitting = ref(false);

const registerForm = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
  agree: false,
});

const registerRules = {
  username: [
    { required: true, message: "请输入用户名", trigger: "blur" },
    { min: 3, max: 20, message: "用户名长度在3到20个字符", trigger: "blur" },
    { pattern: /^[a-zA-Z0-9_]+$/, message: "用户名只能包含字母、数字和下划线", trigger: "blur" },
  ],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, max: 30, message: "密码长度在6到30个字符", trigger: "blur" },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: "密码需包含字母和数字", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认密码", trigger: "blur" },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error("两次输入的密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
  agree: [
    {
      validator: (rule, value, callback) => {
        if (!value) {
          callback(new Error("请同意服务条款和隐私政策"));
        } else {
          callback();
        }
      },
      trigger: "change",
    },
  ],
};

const registerFormRef = ref(null);

const handleRegister = async () => {
  if (!registerFormRef.value) return;

  const valid = await registerFormRef.value.validate().catch(() => false);
  if (!valid) return;

  try {
    isSubmitting.value = true;
    await authStore.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      nickname: registerForm.username,
    });
    ElMessage.success("注册成功");
    router.push("/detection");
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  position: relative;
  overflow: hidden;
}

.register-background {
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
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  top: -150px;
  right: -100px;
  animation: float 8s ease-in-out infinite;
}

.bg-shape-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #3b82f6, #10b981);
  bottom: -100px;
  left: -80px;
  animation: float 10s ease-in-out infinite reverse;
}

.bg-shape-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #ec4899, #f59e0b);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: float 12s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-30px) scale(1.05); }
}

.register-card {
  width: 100%;
  max-width: 440px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-xl);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
  animation: slideUp 0.5s ease-out;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
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

.register-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.register-subtitle {
  font-size: 13px;
  color: #64748b;
  letter-spacing: 0.02em;
}

.register-form {
  margin-bottom: 24px;
}

.register-form :deep(.el-input__wrapper) {
  border-radius: var(--radius-md);
  padding: 12px 16px;
  box-shadow: 0 0 0 1px #e2e8f0;
  transition: all var(--transition-fast);
}

.register-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #cbd5e1;
}

.register-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--primary-color);
}

.agree-terms {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 16px;
}

.agree-terms :deep(.el-checkbox__label) {
  color: #64748b;
}

.terms-link {
  color: var(--primary-color);
  margin: 0 4px;
  transition: color var(--transition-fast);
}

.terms-link:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.register-btn {
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

.register-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.login-link {
  text-align: center;
  font-size: 13px;
  color: #64748b;
}

.login-link a {
  color: var(--primary-color);
  margin-left: 4px;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.login-link a:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

@media (max-width: 480px) {
  .register-card {
    margin: 16px;
    padding: 36px 24px;
  }

  .register-title {
    font-size: 20px;
  }
}
</style>
