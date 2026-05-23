<template>
  <div class="qa-page">
    <div class="page-header">
      <h1 class="page-title">AI 智能问答</h1>
      <p class="page-subtitle">关于遥感目标检测的任何问题，都可以问我</p>
    </div>

    <div class="chat-container">
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'assistant'"><ChatDotRound /></el-icon>
            <el-icon v-else><User /></el-icon>
          </div>
          <div class="message-content">{{ msg.content }}</div>
        </div>
        <div v-if="loading" class="message assistant">
          <div class="message-avatar">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="message-content typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          placeholder="请输入你的问题..."
          @keydown.ctrl.enter="sendMessage"
        />
        <el-button type="primary" :loading="loading" @click="sendMessage">
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from "vue";
import { ChatDotRound, User } from "@element-plus/icons-vue";

const question = ref("");
const loading = ref(false);
const messagesContainer = ref(null);

const messages = ref([
  {
    role: "assistant",
    content: "你好！我是钢铁缺陷检测AI助手。我可以帮你解答关于裂纹、划痕、斑块、麻点、压入、氧化皮等六类缺陷检测的相关问题，也可以为你提供检测结果的详细分析。",
  },
]);

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!question.value.trim() || loading.value) return;

  const userQuestion = question.value.trim();
  messages.value.push({ role: "user", content: userQuestion });
  question.value = "";
  await scrollToBottom();

  loading.value = true;
  
  // 模拟 AI 回复
  setTimeout(() => {
    messages.value.push({
      role: "assistant",
      content: `关于"${userQuestion}"的问题，这是一个遥感目标检测相关的查询。目前系统正在不断完善中，更多功能即将上线。`,
    });
    loading.value = false;
    scrollToBottom();
  }, 1500);
};
</script>

<style scoped>
.qa-page {
  padding: 20px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #666;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f5f5f5;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #27ae60;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #909399;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.message.assistant .message-content {
  background: #fff;
  margin-left: 12px;
}

.message.user .message-content {
  background: #27ae60;
  color: white;
  margin-right: 12px;
}

.typing span {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #999;
  margin: 0 2px;
  animation: typing 1.4s infinite;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-4px);
  }
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
}

.chat-input .el-button {
  align-self: flex-end;
  height: 72px;
}
</style>