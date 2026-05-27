<template>
  <div class="qa-page">
    <div class="page-header">
      <h1 class="page-title">AI 智能问答</h1>
      <p class="page-subtitle">关于钢材表面缺陷检测的任何问题，都可以问我</p>
    </div>

    <div class="chat-container">
      <div class="chat-messages">
        <div class="message ai-message">
          <div class="message-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content">
            你好！我是钢材表面缺陷检测AI助手。我可以帮你解答关于裂纹、夹杂物、斑块、麻面、轧制氧化皮、划痕等六类缺陷检测的相关问题，也可以为你提供检测结果的详细分析。
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="question"
          placeholder="请输入你的问题..."
          :rows="3"
        />
        <el-button type="primary" class="send-btn" :loading="sending">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const question = ref("");
const sending = ref(false);
</script>

<style scoped>
.qa-page {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
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

.chat-container {
  flex: 1;
  background-color: var(--bg-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--border-light);
}

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
}

.message {
  display: flex;
  margin-bottom: 20px;
  animation: slideUp 0.3s ease-out;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.25);
}

.message-content {
  background-color: var(--bg-tertiary);
  padding: 12px 16px;
  border-radius: 0 var(--radius-md) var(--radius-md) var(--radius-md);
  max-width: 70%;
  line-height: 1.6;
  font-size: 14px;
  color: var(--text-primary);
  border: 1px solid var(--border-light);
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-avatar {
  margin-right: 0;
  margin-left: 12px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
}

.user-message .message-content {
  background: linear-gradient(135deg, var(--primary-light) 0%, rgba(99, 102, 241, 0.08) 100%);
  border-radius: var(--radius-md) 0 var(--radius-md) var(--radius-md);
  border-color: rgba(59, 130, 246, 0.15);
}

.chat-input {
  padding: 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 12px;
  background-color: var(--bg-primary);
}

.send-btn {
  width: 100px;
  height: auto;
  border-radius: var(--radius-sm);
  font-weight: 500;
}
</style>
