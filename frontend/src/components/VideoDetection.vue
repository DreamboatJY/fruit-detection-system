<template>
  <div class="video-detection">
    <div class="video-stage">
      <div v-if="!videoUrl" class="video-upload" @click="triggerFileInput">
        <input
          ref="fileInputRef"
          type="file"
          accept="video/*"
          class="video-input"
          @change="handleVideoUpload"
          @click.stop
        />
        <el-icon class="upload-icon"><Monitor /></el-icon>
        <p class="upload-text">点击上传视频</p>
        <p class="upload-desc">支持浏览器可播放的视频格式，推荐 mp4</p>
        <el-button type="primary" size="small">
          <el-icon><Upload /></el-icon>
          选择视频
        </el-button>
      </div>

      <div v-else class="video-content">
        <input
          ref="fileInputRef"
          type="file"
          accept="video/*"
          class="hidden-video-input"
          @change="handleVideoUpload"
        />
        <div ref="videoWrapperRef" class="video-wrapper">
          <video
            ref="videoRef"
            :src="videoUrl"
            class="video-player"
            :controls="!isDetecting"
            @loadedmetadata="handleLoadedMetadata"
            @timeupdate="handleTimeUpdate"
            @ended="stopDetection"
          />
          <canvas ref="canvasRef" class="detection-canvas" />
        </div>

        <div class="video-meta">
          <div class="meta-item">
            <span class="meta-label">视频时长</span>
            <span class="meta-value">{{ formatDuration(videoDuration) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">当前时间</span>
            <span class="meta-value">{{ formatDuration(currentTime) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">检测帧数</span>
            <span class="meta-value">{{ frameIndex }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">当前目标</span>
            <span class="meta-value highlight">{{ currentResult?.total_objects || 0 }}</span>
          </div>
        </div>

        <div class="video-controls">
          <div class="control-item">
            <div class="control-label">
              <span>置信度阈值</span>
              <span>{{ confidenceThreshold.toFixed(2) }}</span>
            </div>
            <el-slider v-model="confidenceThreshold" :min="0.01" :max="0.9" :step="0.01" />
          </div>
          <div class="control-item">
            <div class="control-label">
              <span>检测帧率</span>
              <span>{{ detectionFps }} fps</span>
            </div>
            <el-slider v-model="detectionFps" :min="2" :max="15" :step="1" />
          </div>
          <div class="control-item">
            <div class="control-label">
              <span>IOU 阈值</span>
              <span>{{ iouThreshold.toFixed(2) }}</span>
            </div>
            <el-slider v-model="iouThreshold" :min="0.1" :max="0.95" :step="0.01" />
          </div>
          <div class="button-row">
            <el-button @click="replaceVideo">
              <el-icon><Upload /></el-icon>
              更换视频
            </el-button>
            <el-button
              v-if="!isDetecting"
              type="primary"
              :disabled="!videoUrl"
              @click="startDetection"
            >
              <el-icon><VideoPlay /></el-icon>
              开始检测
            </el-button>
            <el-button v-else type="danger" @click="stopDetection">
              <el-icon><VideoPause /></el-icon>
              停止检测
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";
import { ElMessage } from "element-plus";
import { Monitor, Upload, VideoPause, VideoPlay } from "@element-plus/icons-vue";
import { detectRealtimeFrame } from "../api/detection";

const props = defineProps({
  modelName: {
    type: String,
    default: "rsod-yolo11n",
  },
});

const emit = defineEmits(["result-change", "running-change", "context-change"]);

const fileInputRef = ref(null);
const videoRef = ref(null);
const videoWrapperRef = ref(null);
const canvasRef = ref(null);
const videoUrl = ref("");
const isDetecting = ref(false);
const currentResult = ref(null);
const videoDuration = ref(0);
const currentTime = ref(0);
const frameIndex = ref(0);
const confidenceThreshold = ref(0.25);
const iouThreshold = ref(0.7);
const detectionFps = ref(5);

let detectionTimer = null;
let animationFrameId = null;
let isProcessingFrame = false;
let lastBoxes = [];
let lastImageWidth = 0;
let lastImageHeight = 0;

const colorMap = {
  crazing: "#ef4444",
  inclusion: "#f59e0b",
  patches: "#22c55e",
  pitted_surface: "#3b82f6",
  "rolled-in_scale": "#8b5cf6",
  scratches: "#ec4899",
};

const triggerFileInput = () => {
  fileInputRef.value?.click();
};

const clearCanvas = () => {
  const canvas = canvasRef.value;
  const context = canvas?.getContext("2d");
  if (!canvas || !context) return;
  context.clearRect(0, 0, canvas.width, canvas.height);
};

const syncCanvasSize = () => {
  const wrapper = videoWrapperRef.value;
  const canvas = canvasRef.value;
  if (!wrapper || !canvas) return false;

  const width = wrapper.clientWidth || wrapper.offsetWidth;
  const height = wrapper.clientHeight || wrapper.offsetHeight;
  if (!width || !height) return false;

  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }
  return true;
};

const getRenderedVideoRect = () => {
  const video = videoRef.value;
  const wrapper = videoWrapperRef.value;
  const canvas = canvasRef.value;
  if (!video || !wrapper || !canvas || !video.videoWidth || !video.videoHeight) {
    return null;
  }

  const wrapperRect = wrapper.getBoundingClientRect();
  const videoRect = video.getBoundingClientRect();
  const elementWidth = videoRect.width;
  const elementHeight = videoRect.height;
  if (!elementWidth || !elementHeight) return null;

  const sourceRatio = video.videoWidth / video.videoHeight;
  const elementRatio = elementWidth / elementHeight;
  let renderedWidth = elementWidth;
  let renderedHeight = elementHeight;

  if (elementRatio > sourceRatio) {
    renderedWidth = elementHeight * sourceRatio;
  } else {
    renderedHeight = elementWidth / sourceRatio;
  }

  return {
    x: videoRect.left - wrapperRect.left + (elementWidth - renderedWidth) / 2,
    y: videoRect.top - wrapperRect.top + (elementHeight - renderedHeight) / 2,
    width: renderedWidth,
    height: renderedHeight,
  };
};

const drawDetectionBoxes = (boxes, imageWidth, imageHeight, remember = true) => {
  const canvas = canvasRef.value;
  const context = canvas?.getContext("2d");
  if (!canvas || !context || !syncCanvasSize() || !imageWidth || !imageHeight) return;

  const renderedRect = getRenderedVideoRect();
  if (!renderedRect) return;

  const scaleX = renderedRect.width / imageWidth;
  const scaleY = renderedRect.height / imageHeight;
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.font = "13px Arial";
  context.lineWidth = 2;

  boxes.forEach((box) => {
    const x1 = renderedRect.x + box.x1 * scaleX;
    const y1 = renderedRect.y + box.y1 * scaleY;
    const width = (box.x2 - box.x1) * scaleX;
    const height = (box.y2 - box.y1) * scaleY;
    const color = colorMap[box.class_name] || "#ef4444";
    const label = `${box.chinese_name || box.class_name} ${(box.confidence * 100).toFixed(0)}%`;
    const labelWidth = context.measureText(label).width + 10;
    const labelY = Math.max(0, y1 - 20);

    context.strokeStyle = color;
    context.strokeRect(x1, y1, width, height);
    context.fillStyle = color;
    context.fillRect(x1, labelY, labelWidth, 20);
    context.fillStyle = "#ffffff";
    context.fillText(label, x1 + 5, labelY + 14);
  });

  if (remember) {
    lastBoxes = boxes;
    lastImageWidth = imageWidth;
    lastImageHeight = imageHeight;
  }
};

const animateCanvas = () => {
  if (!isDetecting.value) return;
  if (lastBoxes.length && lastImageWidth && lastImageHeight) {
    drawDetectionBoxes(lastBoxes, lastImageWidth, lastImageHeight, false);
  }
  animationFrameId = window.requestAnimationFrame(animateCanvas);
};

const captureAndDetectFrame = async () => {
  const video = videoRef.value;
  if (!video || video.paused || video.ended || isProcessingFrame) return;
  if (!video.videoWidth || !video.videoHeight) return;

  isProcessingFrame = true;
  try {
    const tempCanvas = document.createElement("canvas");
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const context = tempCanvas.getContext("2d");
    context.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);

    const blob = await new Promise((resolve) => {
      tempCanvas.toBlob(resolve, "image/jpeg", 0.6);
    });
    if (!blob) return;

    const formData = new FormData();
    formData.append("file", blob, "frame.jpg");
    formData.append("model_name", props.modelName);
    formData.append("confidence_threshold", String(confidenceThreshold.value));
    formData.append("iou_threshold", String(iouThreshold.value));

    const response = await detectRealtimeFrame(formData);
    if (response.success && response.data) {
      currentResult.value = response.data;
      frameIndex.value += 1;
      emit("result-change", response.data);
      drawDetectionBoxes(
        response.data.boxes || [],
        response.data.image_width,
        response.data.image_height,
      );
    }
  } catch (error) {
    console.error("视频帧检测失败:", error);
  } finally {
    isProcessingFrame = false;
  }
};

const startDetection = async () => {
  const video = videoRef.value;
  if (!video) return;

  isDetecting.value = true;
  currentResult.value = null;
  frameIndex.value = 0;
  lastBoxes = [];
  emit("running-change", true);
  emit("result-change", null);
  await nextTick();
  syncCanvasSize();

  try {
    await video.play();
  } catch (error) {
    ElMessage.warning("自动播放被阻止，请手动播放视频");
  }

  animateCanvas();
  await captureAndDetectFrame();
  const intervalMs = Math.floor(1000 / detectionFps.value);
  detectionTimer = window.setInterval(captureAndDetectFrame, intervalMs);
};

const stopDetection = () => {
  if (detectionTimer) {
    window.clearInterval(detectionTimer);
    detectionTimer = null;
  }
  if (animationFrameId) {
    window.cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }
  videoRef.value?.pause();
  isDetecting.value = false;
  isProcessingFrame = false;
  lastBoxes = [];
  clearCanvas();
  emit("running-change", false);
};

const revokeVideoUrl = () => {
  if (videoUrl.value) {
    URL.revokeObjectURL(videoUrl.value);
    videoUrl.value = "";
  }
};

const resetState = () => {
  stopDetection();
  currentResult.value = null;
  videoDuration.value = 0;
  currentTime.value = 0;
  frameIndex.value = 0;
  emit("result-change", null);
  emit("context-change", false);
};

const handleVideoUpload = async (event) => {
  const file = event.target.files?.[0];
  event.target.value = "";
  if (!file) return;

  resetState();
  revokeVideoUrl();
  videoUrl.value = URL.createObjectURL(file);
  emit("context-change", true);
  await nextTick();
  syncCanvasSize();
};

const replaceVideo = () => {
  triggerFileInput();
};

const handleLoadedMetadata = () => {
  videoDuration.value = videoRef.value?.duration || 0;
  syncCanvasSize();
};

const handleTimeUpdate = () => {
  currentTime.value = videoRef.value?.currentTime || 0;
};

const formatDuration = (seconds) => {
  if (!Number.isFinite(seconds)) return "00:00";
  const minutes = Math.floor(seconds / 60);
  const rest = Math.floor(seconds % 60);
  return `${String(minutes).padStart(2, "0")}:${String(rest).padStart(2, "0")}`;
};

defineExpose({
  stopDetection,
});

onBeforeUnmount(() => {
  resetState();
  revokeVideoUrl();
});
</script>

<style scoped>
.video-detection {
  height: 100%;
}

.video-stage {
  height: 100%;
  min-height: 420px;
}

.video-upload {
  position: relative;
  display: flex;
  height: 100%;
  min-height: 420px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  background-color: #f9fafb;
  cursor: pointer;
}

.video-upload:hover {
  border-color: var(--primary-color);
  background-color: var(--primary-light);
}

.video-input {
  position: absolute;
  inset: 0;
  z-index: 10;
  opacity: 0;
  cursor: pointer;
}

.hidden-video-input {
  display: none;
}

.upload-icon {
  margin-bottom: 12px;
  font-size: 52px;
  color: #9ca3af;
}

.upload-text {
  margin-bottom: 4px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.upload-desc {
  margin-bottom: 18px;
  font-size: 13px;
  color: var(--text-secondary);
}

.video-content {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.video-wrapper {
  position: relative;
  overflow: hidden;
  width: 100%;
  border-radius: 8px;
  background-color: #000000;
}

.video-player {
  display: block;
  width: 100%;
  height: auto;
  max-height: 460px;
  object-fit: contain;
}

.detection-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.video-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 6px;
  background-color: #f9fafb;
}

.meta-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.meta-value {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.meta-value.highlight {
  color: var(--primary-color);
}

.video-controls {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) auto;
  align-items: end;
  gap: 16px;
}

.control-item {
  min-width: 0;
}

.control-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
  font-size: 13px;
  color: var(--text-secondary);
}

.button-row {
  display: flex;
  gap: 8px;
  padding-bottom: 1px;
}

@media (max-width: 960px) {
  .video-meta,
  .video-controls {
    grid-template-columns: 1fr 1fr;
  }

  .button-row {
    grid-column: 1 / -1;
  }
}
</style>
