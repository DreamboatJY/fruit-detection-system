<template>
  <div class="camera-page">
    <div class="page-header">
      <div class="breadcrumb">
        <span>工作台</span>
        <span class="separator">›</span>
        <span class="active">摄像头实时检测</span>
      </div>
      <h1 class="page-title">开启摄像头，实时识别目标</h1>
      <p class="page-subtitle">
        基于WebSocket实时传输，逐帧检测并返回标注结果
      </p>
    </div>

    <div class="camera-controls">
      <el-button
        type="primary"
        :loading="isConnecting"
        :disabled="isStreaming"
        @click="startCamera"
      >
        <el-icon><VideoCamera /></el-icon>
        {{ isConnecting ? '连接中...' : '开启摄像头' }}
      </el-button>
      <el-button
        type="danger"
        :disabled="!isStreaming"
        @click="stopCamera"
      >
        <el-icon><VideoPause /></el-icon>
        停止检测
      </el-button>
      <el-select v-model="selectedModel" style="width: 150px" :disabled="isStreaming">
        <el-option label="pest-v1" value="pest-v1" />
        <el-option label="pest-v2" value="pest-v2" />
      </el-select>
    </div>

    <div class="main-content">
      <div class="left-panel">
        <div class="panel-header">
          <span class="panel-title">实时预览</span>
          <el-tag v-if="isStreaming" type="success" effect="light" class="status-tag">
            <el-icon class="el-icon--left"><VideoCamera /></el-icon>
            检测中
          </el-tag>
          <el-tag v-else type="info" effect="light" class="status-tag">
            <el-icon class="el-icon--left"><VideoPause /></el-icon>
            未连接
          </el-tag>
        </div>

        <div class="video-container">
          <video
            ref="videoRef"
            autoplay
            playsinline
            muted
            class="video-element"
          ></video>
          <canvas ref="canvasRef" class="canvas-element" style="display: none;"></canvas>
          <img
            v-if="annotatedImage"
            :src="annotatedImage"
            alt="检测结果"
            class="annotated-image"
          />
          <div v-if="!isStreaming && !annotatedImage" class="placeholder">
            <el-icon :size="48"><VideoCamera /></el-icon>
            <p>点击"开启摄像头"开始实时检测</p>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="info-card">
          <div class="info-item">
            <span class="info-label">检测模型</span>
            <span class="info-value">{{ selectedModel }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">帧率</span>
            <span class="info-value">{{ fps }} FPS</span>
          </div>
          <div class="info-item">
            <span class="info-label">延迟</span>
            <span class="info-value">{{ latency }} ms</span>
          </div>
        </div>

        <div class="result-card">
          <div class="card-header">
            <el-icon><List /></el-icon>
            <span class="card-title">当前帧检测结果</span>
          </div>
          <div v-if="currentBoxes.length === 0" class="empty-state">
            <el-icon class="empty-icon"><CircleCheck /></el-icon>
            <p class="empty-text">未检测到目标</p>
          </div>
          <div v-else class="detection-list">
            <div
              v-for="(box, index) in currentBoxes"
              :key="index"
              class="detection-item"
            >
              <span class="item-name">{{ box.class_name }}</span>
              <span class="item-confidence">{{ (box.confidence * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <div class="stats-card">
          <div class="card-header">
            <el-icon><DataAnalysis /></el-icon>
            <span class="card-title">检测统计</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ totalFrames }}</span>
              <span class="stat-label">总帧数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ totalObjects }}</span>
              <span class="stat-label">检测目标</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from "vue";
import { ElMessage } from "element-plus";
import {
  VideoCamera,
  VideoPause,
  List,
  CircleCheck,
  DataAnalysis,
} from "@element-plus/icons-vue";

const videoRef = ref(null);
const canvasRef = ref(null);
const selectedModel = ref("pest-v1");
const isStreaming = ref(false);
const isConnecting = ref(false);
const annotatedImage = ref(null);
const currentBoxes = ref([]);
const fps = ref(0);
const latency = ref(0);
const totalFrames = ref(0);
const totalObjects = ref(0);

let stream = null;
let ws = null;
let animationId = null;
let frameCount = 0;
let lastFpsTime = 0;

const WS_URL = "ws://localhost:8000/ws/camera/detect";

const startCamera = async () => {
  try {
    isConnecting.value = true;

    // 获取摄像头权限
    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: "user"
      }
    });

    videoRef.value.srcObject = stream;

    // 等待视频加载
    await new Promise((resolve) => {
      videoRef.value.onloadedmetadata = () => {
        videoRef.value.play();
        resolve();
      };
    });

    // 建立WebSocket连接
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log("WebSocket连接已建立");
      isStreaming.value = true;
      isConnecting.value = false;
      ElMessage.success("摄像头已开启，开始实时检测");
      startDetection();
    };

    ws.onmessage = (event) => {
      const result = JSON.parse(event.data);
      handleDetectionResult(result);
    };

    ws.onerror = (error) => {
      console.error("WebSocket错误:", error);
      ElMessage.error("WebSocket连接错误");
    };

    ws.onclose = () => {
      console.log("WebSocket连接已关闭");
      isStreaming.value = false;
    };

  } catch (error) {
    console.error("开启摄像头失败:", error);
    ElMessage.error(error.message || "开启摄像头失败，请检查权限设置");
    isConnecting.value = false;
  }
};

const startDetection = () => {
  const canvas = canvasRef.value;
  const video = videoRef.value;
  const ctx = canvas.getContext("2d");

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const sendFrame = () => {
    if (!isStreaming.value || !ws || ws.readyState !== WebSocket.OPEN) {
      return;
    }

    // 绘制当前视频帧到canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // 转换为base64
    const frameData = canvas.toDataURL("image/jpeg", 0.8).split(",")[1];

    // 发送帧数据
    ws.send(JSON.stringify({
      frame: frameData,
      model_name: selectedModel.value
    }));

    // 统计帧率
    frameCount++;
    const now = Date.now();
    if (now - lastFpsTime >= 1000) {
      fps.value = frameCount;
      frameCount = 0;
      lastFpsTime = now;
    }

    // 控制发送频率（约10fps）
    setTimeout(() => {
      animationId = requestAnimationFrame(sendFrame);
    }, 100);
  };

  lastFpsTime = Date.now();
  sendFrame();
};

const handleDetectionResult = (result) => {
  if (!result.success) {
    console.error("检测失败:", result.error);
    return;
  }

  // 更新标注图像
  if (result.annotated_frame) {
    annotatedImage.value = `data:image/jpeg;base64,${result.annotated_frame}`;
  }

  // 更新检测结果
  currentBoxes.value = result.boxes || [];
  totalObjects.value += result.total_objects || 0;
  totalFrames.value++;

  // 计算延迟
  latency.value = Math.round(result.detection_time * 1000);
};

const stopCamera = () => {
  isStreaming.value = false;

  // 停止动画帧
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }

  // 关闭WebSocket
  if (ws) {
    ws.close();
    ws = null;
  }

  // 停止摄像头
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
  }

  // 清理状态
  videoRef.value.srcObject = null;
  annotatedImage.value = null;
  currentBoxes.value = [];
  fps.value = 0;
  latency.value = 0;
  totalFrames.value = 0;
  totalObjects.value = 0;
  frameCount = 0;

  ElMessage.info("已停止检测");
};

onUnmounted(() => {
  stopCamera();
});
</script>

<style scoped>
.camera-page {
  width: 100%;
  position: relative;
}

.page-header {
  margin-bottom: 32px;
  padding-top: 0;
}

.breadcrumb {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.separator {
  margin: 0 6px;
}

.active {
  color: var(--text-primary);
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

.camera-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: center;
}

.main-content {
  display: flex;
  gap: 24px;
}

.left-panel {
  flex: 1;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 20px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.video-container {
  position: relative;
  width: 100%;
  height: 480px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: none;
}

.canvas-element {
  display: none;
}

.annotated-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  text-align: center;
  color: #999;
}

.placeholder .el-icon {
  margin-bottom: 8px;
}

.right-panel {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card,
.result-card,
.stats-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.info-value {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.card-header .el-icon {
  font-size: 16px;
  color: var(--primary-color);
  margin-right: 8px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0;
}

.empty-icon {
  font-size: 48px;
  color: var(--success-color);
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.detection-list {
  max-height: 200px;
  overflow-y: auto;
}

.detection-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detection-item:last-child {
  border-bottom: none;
}

.item-name {
  font-size: 14px;
  color: var(--text-primary);
}

.item-confidence {
  font-size: 13px;
  color: var(--primary-color);
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
