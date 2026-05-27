<template>
  <div class="camera-detection">
    <div class="camera-stage">
      <video
        ref="videoRef"
        class="camera-video"
        autoplay
        muted
        playsinline
      ></video>
      <canvas ref="overlayCanvasRef" class="camera-overlay"></canvas>
      <canvas ref="captureCanvasRef" class="capture-canvas"></canvas>

      <div v-if="!isRunning" class="camera-placeholder">
        <el-icon class="placeholder-icon"><VideoCamera /></el-icon>
        <p class="placeholder-title">摄像头实时检测</p>
        <p class="placeholder-desc">开启后将在本地采集画面，并发送单帧到后端检测</p>
      </div>
    </div>

    <div class="camera-toolbar">
      <div class="camera-actions">
        <el-button type="primary" :disabled="isRunning" @click="startCamera">
          <el-icon><VideoPlay /></el-icon>
          开始
        </el-button>
        <el-button :disabled="!isRunning" @click="togglePause">
          <el-icon><component :is="isPaused ? VideoPlay : VideoPause" /></el-icon>
          {{ isPaused ? "恢复" : "暂停" }}
        </el-button>
        <el-button :disabled="!isRunning" @click="stopCamera">
          <el-icon><CircleClose /></el-icon>
          停止
        </el-button>
      </div>
      <el-tag :type="statusTagType" effect="light">{{ statusText }}</el-tag>
    </div>

    <div class="camera-settings">
      <div class="setting-item profile-setting">
        <span class="setting-label">视频规格</span>
        <el-select v-model="selectedProfileKey" :disabled="isRunning" size="small">
          <el-option
            v-for="profile in videoProfiles"
            :key="profile.key"
            :label="profile.label"
            :value="profile.key"
          />
        </el-select>
      </div>
      <div class="setting-item">
        <span class="setting-label">置信度 {{ Math.round(confidenceThreshold * 100) }}%</span>
        <el-slider v-model="confidenceThreshold" :min="0.1" :max="0.9" :step="0.05" size="small" />
      </div>
      <div class="setting-item">
        <span class="setting-label">IOU {{ Math.round(iouThreshold * 100) }}%</span>
        <el-slider v-model="iouThreshold" :min="0.1" :max="0.9" :step="0.05" size="small" />
      </div>
      <div class="setting-item">
        <span class="setting-label">推理间隔 {{ inferenceInterval }} 帧</span>
        <el-slider v-model="inferenceInterval" :min="1" :max="6" :step="1" size="small" />
      </div>
    </div>

    <div class="camera-stats">
      <div class="stat-item">
        <span class="stat-value">{{ totalObjects }}</span>
        <span class="stat-label">目标数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ formatNumber(detectionTime) }}s</span>
        <span class="stat-label">推理耗时</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ formatNumber(fps) }}</span>
        <span class="stat-label">后端 FPS</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ frameIndex }}</span>
        <span class="stat-label">帧序号</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref } from "vue";
import { ElMessage } from "element-plus";
import {
  CircleClose,
  VideoCamera,
  VideoPause,
  VideoPlay,
} from "@element-plus/icons-vue";
import { detectFrame } from "../api/detection";

const emit = defineEmits(["result-change", "running-change"]);

const videoRef = ref(null);
const overlayCanvasRef = ref(null);
const captureCanvasRef = ref(null);
const isRunning = ref(false);
const isPaused = ref(false);
const isDetecting = ref(false);
const currentBoxes = ref([]);
const frameIndex = ref(0);
const fps = ref(0);
const detectionTime = ref(0);
const totalObjects = ref(0);
const errorMessage = ref("");
const confidenceThreshold = ref(0.5);
const iouThreshold = ref(0.45);
const inferenceInterval = ref(2);
const selectedProfileKey = ref("standard");

const videoProfiles = [
  {
    key: "smooth",
    label: "流畅 480p / 24fps",
    width: 640,
    height: 360,
    frameRate: 24,
    imageSize: 320,
    jpegQuality: 0.65,
  },
  {
    key: "standard",
    label: "标准 640x480 / 30fps",
    width: 640,
    height: 480,
    frameRate: 30,
    imageSize: 320,
    jpegQuality: 0.7,
  },
  {
    key: "hd",
    label: "高清 720p / 30fps",
    width: 1280,
    height: 720,
    frameRate: 30,
    imageSize: 416,
    jpegQuality: 0.75,
  },
];

let videoStream = null;
let detectionFrameId = null;
let drawFrameId = null;
let lastDetectionTime = 0;
let consecutiveErrorCount = 0;

const selectedProfile = computed(() => {
  return videoProfiles.find((profile) => profile.key === selectedProfileKey.value) || videoProfiles[1];
});

const targetInterval = computed(() => {
  return (inferenceInterval.value * 1000) / selectedProfile.value.frameRate;
});

const statusText = computed(() => {
  if (errorMessage.value) return "异常";
  if (!isRunning.value) return "未开启";
  if (isPaused.value) return "已暂停";
  if (isDetecting.value) return "检测中";
  return "运行中";
});

const statusTagType = computed(() => {
  if (errorMessage.value) return "danger";
  if (!isRunning.value) return "info";
  if (isPaused.value) return "warning";
  return "success";
});

const startCamera = async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    ElMessage.error("当前浏览器不支持摄像头访问");
    return;
  }

  try {
    errorMessage.value = "";
    await nextTick();
    const profile = selectedProfile.value;
    videoStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: profile.width },
        height: { ideal: profile.height },
        frameRate: { ideal: profile.frameRate },
      },
      audio: false,
    });

    if (!videoRef.value) return;
    videoRef.value.srcObject = videoStream;
    videoRef.value.onloadedmetadata = () => {
      initCanvas();
      isRunning.value = true;
      isPaused.value = false;
      emit("running-change", true);
      startDrawingLoop();
      startDetectionLoop();
    };
  } catch (error) {
    handleCameraError(error);
  }
};

const stopCamera = () => {
  cancelLoops();
  if (videoStream) {
    videoStream.getTracks().forEach((track) => track.stop());
    videoStream = null;
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null;
  }
  isRunning.value = false;
  isPaused.value = false;
  isDetecting.value = false;
  currentBoxes.value = [];
  totalObjects.value = 0;
  detectionTime.value = 0;
  fps.value = 0;
  frameIndex.value = 0;
  consecutiveErrorCount = 0;
  clearOverlay();
  emitResult();
  emit("running-change", false);
};

const togglePause = () => {
  if (!isRunning.value) return;
  isPaused.value = !isPaused.value;
};

const initCanvas = () => {
  const video = videoRef.value;
  const overlayCanvas = overlayCanvasRef.value;
  const captureCanvas = captureCanvasRef.value;
  if (!video || !overlayCanvas || !captureCanvas) return;

  const width = video.videoWidth || 640;
  const height = video.videoHeight || 480;
  overlayCanvas.width = width;
  overlayCanvas.height = height;
  captureCanvas.width = width;
  captureCanvas.height = height;
};

const startDetectionLoop = () => {
  cancelAnimationFrame(detectionFrameId);
  lastDetectionTime = 0;
  sendFrameForDetection();
};

const sendFrameForDetection = async () => {
  if (!isRunning.value) return;

  const now = performance.now();
  if (!isPaused.value && !isDetecting.value && now - lastDetectionTime >= targetInterval.value) {
    await detectCurrentFrame(now);
  }

  detectionFrameId = requestAnimationFrame(sendFrameForDetection);
};

const detectCurrentFrame = async (currentTime) => {
  const video = videoRef.value;
  const captureCanvas = captureCanvasRef.value;
  if (!video || !captureCanvas || !video.videoWidth || !video.videoHeight) return;

  const ctx = captureCanvas.getContext("2d");
  ctx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
  const imageData = captureCanvas.toDataURL("image/jpeg", selectedProfile.value.jpegQuality);

  try {
    isDetecting.value = true;
    const response = await detectFrame({
      image: imageData,
      confidence_threshold: confidenceThreshold.value,
      iou_threshold: iouThreshold.value,
      model_image_size: selectedProfile.value.imageSize,
    });
    if (!isRunning.value) return;
    if (response.success && response.data) {
      currentBoxes.value = response.data.boxes || [];
      frameIndex.value = response.data.frame_index || frameIndex.value;
      fps.value = response.data.fps || fps.value;
      detectionTime.value = response.data.detection_time || 0;
      totalObjects.value = response.data.total_objects || 0;
      consecutiveErrorCount = 0;
      errorMessage.value = "";
      lastDetectionTime = currentTime;
      emitResult();
    } else {
      handleDetectionError(response.message || "检测失败");
    }
  } catch (error) {
    if (!isRunning.value) return;
    handleDetectionError(error.message || "网络请求失败");
  } finally {
    isDetecting.value = false;
  }
};

const startDrawingLoop = () => {
  cancelAnimationFrame(drawFrameId);
  drawBoxes();
};

const drawBoxes = () => {
  if (!isRunning.value) return;
  const canvas = overlayCanvasRef.value;
  const video = videoRef.value;
  if (!canvas || !video) {
    drawFrameId = requestAnimationFrame(drawBoxes);
    return;
  }

  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const scaleX = canvas.width / (video.videoWidth || canvas.width);
  const scaleY = canvas.height / (video.videoHeight || canvas.height);

  currentBoxes.value.forEach((box) => {
    const x1 = box.x1 * scaleX;
    const y1 = box.y1 * scaleY;
    const x2 = box.x2 * scaleX;
    const y2 = box.y2 * scaleY;
    const width = x2 - x1;
    const height = y2 - y1;
    const color = getBoxColor(box.class_name);
    const label = `${box.chinese_name || box.class_name} ${(box.confidence * 100).toFixed(0)}%`;

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.strokeRect(x1, y1, width, height);
    ctx.fillStyle = color;
    ctx.globalAlpha = 0.12;
    ctx.fillRect(x1, y1, width, height);
    ctx.globalAlpha = 1;

    ctx.font = "12px Arial";
    const labelWidth = Math.min(ctx.measureText(label).width + 10, canvas.width - x1);
    const labelHeight = 18;
    const labelY = y1 >= labelHeight ? y1 - labelHeight : y1 + height;
    ctx.fillStyle = color;
    ctx.fillRect(x1, labelY, labelWidth, labelHeight);
    ctx.fillStyle = "#ffffff";
    ctx.fillText(label, x1 + 5, labelY + 13);
  });

  drawFrameId = requestAnimationFrame(drawBoxes);
};

const clearOverlay = () => {
  const canvas = overlayCanvasRef.value;
  if (!canvas) return;
  canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
};

const cancelLoops = () => {
  if (detectionFrameId) cancelAnimationFrame(detectionFrameId);
  if (drawFrameId) cancelAnimationFrame(drawFrameId);
  detectionFrameId = null;
  drawFrameId = null;
};

const handleCameraError = (error) => {
  console.error("摄像头错误:", error);
  const messages = {
    NotAllowedError: "摄像头权限被拒绝，请在浏览器设置中允许访问",
    NotFoundError: "未检测到摄像头设备，请检查设备连接",
    NotReadableError: "摄像头被其他应用占用，请关闭其他应用后重试",
  };
  errorMessage.value = messages[error.name] || "无法访问摄像头，请检查设备和权限设置";
  ElMessage.error(errorMessage.value);
  stopCamera();
};

const handleDetectionError = (message) => {
  consecutiveErrorCount += 1;
  errorMessage.value = message;
  if (consecutiveErrorCount === 1 || consecutiveErrorCount >= 5) {
    ElMessage.error(message);
  }
  if (consecutiveErrorCount >= 5) {
    stopCamera();
  }
};

const emitResult = () => {
  emit("result-change", {
    boxes: currentBoxes.value,
    total_objects: totalObjects.value,
    detection_time: detectionTime.value,
    model_name: "neu-det-yolo11n",
    frame_index: frameIndex.value,
    fps: fps.value,
  });
};

const getBoxColor = (className) => {
  const colors = {
    crazing: "#ef4444",          // 裂纹 - 红色
    inclusion: "#f59e0b",        // 夹杂物 - 橙色
    patches: "#10b981",          // 斑块 - 绿色
    pitted_surface: "#3b82f6",   // 麻面 - 蓝色
    "rolled-in_scale": "#8b5cf6", // 轧制氧化皮 - 紫色
    scratches: "#ec4899",        // 划痕 - 粉色
  };
  return colors[className] || "#6b7280";
};

const formatNumber = (value) => {
  const number = Number(value);
  return Number.isFinite(number) ? number.toFixed(2) : "0.00";
};

onBeforeUnmount(() => {
  stopCamera();
});

defineExpose({
  stopCamera,
});
</script>

<style scoped>
.camera-detection {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.camera-stage {
  position: relative;
  width: 100%;
  height: 420px;
  overflow: hidden;
  border-radius: 8px;
  background-color: #111827;
}

.camera-video,
.camera-overlay {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.camera-overlay {
  pointer-events: none;
}

.capture-canvas {
  display: none;
}

.camera-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  text-align: center;
  color: #ffffff;
  background-color: #111827;
}

.placeholder-icon {
  font-size: 52px;
  margin-bottom: 14px;
  color: #60a5fa;
}

.placeholder-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
}

.placeholder-desc {
  max-width: 360px;
  font-size: 13px;
  color: #cbd5e1;
  line-height: 1.6;
}

.camera-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.camera-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.camera-settings {
  display: grid;
  grid-template-columns: 180px repeat(3, minmax(0, 1fr));
  gap: 12px;
  align-items: center;
  padding: 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background-color: #ffffff;
}

.setting-item {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.setting-label {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.2;
}

.profile-setting :deep(.el-select) {
  width: 100%;
}

.camera-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border-radius: 8px;
  background-color: #f9fafb;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-label {
  margin-top: 5px;
  font-size: 12px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .camera-stage {
    height: 300px;
  }

  .camera-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .camera-settings {
    grid-template-columns: 1fr;
  }

  .camera-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
