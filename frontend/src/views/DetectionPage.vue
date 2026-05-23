<template>
  <div class="detection-page">
    <div class="page-header">
      <div class="breadcrumb">
        <span>工作台</span>
        <span class="separator">›</span>
        <span class="active">智能检测</span>
      </div>
      <h1 class="page-title">上传钢材表面图片，立即检测缺陷类型</h1>
      <p class="page-subtitle">
        支持裂纹、划痕、斑块、麻点、压入、氧化皮等6类缺陷检测
      </p>
    </div>

    <div class="model-selector">
      <el-select v-model="selectedModel" style="width: 180px">
        <el-option label="pest-v1" value="pest-v1" />
        <el-option label="pest-v2" value="pest-v2" />
      </el-select>
    </div>

    <div class="function-tabs">
      <div
        v-for="tab in functionTabs"
        :key="tab.key"
        class="function-tab"
        :class="{ active: activeTab === tab.key }"
        @click="handleTabClick(tab.key)"
      >
        <el-icon :size="18" class="tab-icon"><component :is="tab.icon" /></el-icon>
        <div class="tab-content">
          <span class="tab-text">{{ tab.name }}</span>
          <span class="tab-desc">{{ tab.desc }}</span>
        </div>
      </div>
    </div>

    <!-- 隐藏的文件输入 -->
    <input
      ref="singleInputRef"
      type="file"
      accept="image/*"
      class="hidden-input"
      @change="handleFileChange($event, 'single')"
    />
    <input
      ref="batchInputRef"
      type="file"
      accept="image/*"
      multiple
      class="hidden-input"
      @change="handleFileChange($event, 'batch')"
    />

    <div class="main-content">
      <!-- 单图/批量检测面板 -->
      <template v-if="activeTab === 'single' || activeTab === 'batch'">
        <div class="left-panel">
          <div class="panel-header">
            <span class="panel-title">检测预览</span>
            <el-tag v-if="detectionResult" type="success" effect="light" class="result-tag">
              <el-icon class="el-icon--left"><Check /></el-icon>
              检测完成
            </el-tag>
          </div>

          <div class="toolbar">
            <el-button
              :class="{ active: compareMode === 'side' }"
              size="small"
              @click="compareMode = 'side'"
            >
              <el-icon><Minus /></el-icon>
              并排对比
            </el-button>
          </div>

          <div class="image-compare">
            <div class="image-card">
              <img
                v-if="originalImage"
                :src="originalImage"
                alt="原始图片"
                class="compare-image"
              />
              <div v-else class="placeholder-image">
                <el-icon :size="48"><Picture /></el-icon>
                <p>等待上传图片</p>
              </div>
              <div class="image-label">原始图片</div>
            </div>
            <div class="image-card">
              <img
                v-if="resultImage"
                :src="resultImage"
                alt="检测结果"
                class="compare-image"
              />
              <div v-else class="placeholder-image">
                <el-icon :size="48"><Camera /></el-icon>
                <p>等待检测</p>
              </div>
              <div class="image-label">检测结果</div>
              <div v-if="detectionResult" class="detection-mark"></div>
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
              <span class="info-label">检测耗时</span>
              <span class="info-value">{{ detectionResult?.detection_time || '-' }} s</span>
            </div>
          </div>

          <div class="result-card">
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span class="card-title">识别清单</span>
            </div>
            <div v-if="!detectionResult || detectionResult.total_objects === 0" class="empty-state">
              <el-icon class="empty-icon"><CircleCheck /></el-icon>
              <p class="empty-text">未检测到目标</p>
              <p class="empty-desc">请上传图片进行检测</p>
            </div>
            <div v-else class="detection-list">
              <div
                v-for="(box, index) in detectionResult.boxes"
                :key="index"
                class="detection-item"
              >
                <span class="item-name">{{ box.class_name }}</span>
                <span class="item-confidence">{{ (box.confidence * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>

          <div v-if="batchResults.length > 0" class="result-card">
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span class="card-title">批量检测结果</span>
            </div>

            <div class="batch-list">
              <div
                v-for="(item, index) in batchResults"
                :key="index"
                class="batch-item"
                @click="showBatchResult(item)"
              >
                <div class="batch-filename">{{ item.filename }}</div>
                <div class="batch-count">
                  {{ item.data?.total_objects || 0 }} 个目标
                </div>
              </div>
            </div>
          </div>

          <div class="result-card">
            <div class="card-header">
              <el-icon><ChatDotRound /></el-icon>
              <span class="card-title">AI 诊断建议</span>
            </div>
            <div class="diagnosis-content">
              <p v-if="!detectionResult">等待检测...</p>
              <p v-else>
                检测到 {{ detectionResult.total_objects }} 个目标，耗时 {{ detectionResult.detection_time }} 秒。
                请及时关注产品质量。
              </p>
            </div>
          </div>

          <div class="action-buttons">
            <el-button size="default" class="btn-secondary" @click="handleRedetect" :loading="isDetecting">
              <el-icon><Refresh /></el-icon>
              {{ isDetecting ? '检测中...' : '重新检测' }}
            </el-button>
          </div>
        </div>
      </template>

      <!-- 摄像头实时检测面板 -->
      <template v-else-if="activeTab === 'folder'">
        <div class="camera-panel">
          <div class="camera-controls">
            <el-button
              type="primary"
              :loading="isConnecting"
              :disabled="isStreaming"
              @click="startCamera"
            >
              <el-icon><Camera /></el-icon>
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

          <div class="camera-content">
            <div class="camera-left">
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
                  <el-icon :size="48"><Camera /></el-icon>
                  <p>点击"开启摄像头"开始实时检测</p>
                </div>
              </div>
            </div>

            <div class="camera-right">
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

              <div class="result-card">
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

      <!-- 视频检测面板 -->
      <template v-else-if="activeTab === 'video'">
        <div class="video-panel">
          <div class="video-header">
            <h3>视频检测</h3>
            <div class="video-actions">
              <el-select v-model="selectedModel" style="width: 150px" :disabled="isDetecting">
                <el-option label="pest-v1" value="pest-v1" />
                <el-option label="pest-v2" value="pest-v2" />
              </el-select>
              <el-button type="primary" @click="videoInputRef?.click()" :disabled="isDetecting">
                <el-icon><Upload /></el-icon>
                上传视频
              </el-button>
            </div>
          </div>

          <input
            ref="videoInputRef"
            type="file"
            accept="video/*"
            class="hidden-input"
            @change="handleVideoChange"
          />

          <div v-if="!videoResult && !isDetecting" class="video-placeholder">
            <el-icon :size="64"><Monitor /></el-icon>
            <p>上传视频文件开始检测</p>
            <p class="video-hint">支持 MP4、AVI、MOV 等常见视频格式</p>
          </div>

          <div v-if="isDetecting" class="video-progress">
            <el-progress
              :percentage="videoProgress"
              :status="videoProgress === 100 ? 'success' : ''"
              :stroke-width="20"
            />
            <p class="progress-text">正在处理第 {{ videoCurrentFrame }} / {{ videoTotalFrames }} 帧...</p>
          </div>

          <div v-if="videoResult" class="video-result">
            <div class="video-info">
              <div class="info-card">
                <div class="info-item">
                  <span class="info-label">检测模型</span>
                  <span class="info-value">{{ videoResult.model_name }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">检测耗时</span>
                  <span class="info-value">{{ videoResult.detection_time }} s</span>
                </div>
                <div class="info-item">
                  <span class="info-label">总帧数</span>
                  <span class="info-value">{{ videoResult.total_frames }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">检测目标</span>
                  <span class="info-value">{{ videoResult.total_objects }}</span>
                </div>
              </div>

              <div class="result-card">
                <div class="card-header">
                  <el-icon><DataAnalysis /></el-icon>
                  <span class="card-title">检测统计</span>
                </div>
                <div v-if="Object.keys(videoResult.detection_stats || {}).length === 0" class="empty-state">
                  <el-icon class="empty-icon"><CircleCheck /></el-icon>
                  <p class="empty-text">未检测到目标</p>
                </div>
                <div v-else class="detection-list">
                  <div
                    v-for="(count, name) in videoResult.detection_stats"
                    :key="name"
                    class="detection-item"
                  >
                    <span class="item-name">{{ name }}</span>
                    <span class="item-confidence">{{ count }} 次</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="video-player">
              <video
                :src="`http://localhost:8000${videoResult.result_video_url}`"
                controls
                class="result-video"
              ></video>
              <div class="video-label">检测结果视频</div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onUnmounted } from "vue";
import { ElMessage, ElLoading } from "element-plus";
import {
  Picture,
  Plus,
  Folder,
  Monitor,
  Check,
  Grid,
  List,
  CircleCheck,
  ChatDotRound,
  Refresh,
  Minus,
  Camera,
  VideoPause,
  DataAnalysis,
} from "@element-plus/icons-vue";
import { detectSingleImage, detectBatchImages, detectVideo } from "../api/detection";

const selectedModel = ref("pest-v1");
const activeTab = ref("single");
const compareMode = ref("side");
const originalImage = ref(null);
const resultImage = ref(null);
const detectionResult = ref(null);
const isDetecting = ref(false);
const batchResults = ref([]);
const singleInputRef = ref(null);
const batchInputRef = ref(null);
const videoInputRef = ref(null);

// 视频检测相关状态
const videoResult = ref(null);
const videoProgress = ref(0);
const videoCurrentFrame = ref(0);
const videoTotalFrames = ref(0);

// 摄像头相关状态
const videoRef = ref(null);
const canvasRef = ref(null);
const isStreaming = ref(false);
const isConnecting = ref(false);
const annotatedImage = ref(null);
const currentBoxes = ref([]);
const fps = ref(0);
const latency = ref(0);
const totalFrames = ref(0);
const totalObjects = ref(0);

let cameraStream = null;
let cameraWs = null;
let cameraAnimationId = null;
let frameCount = 0;
let lastFpsTime = 0;

const WS_URL = "ws://localhost:8000/api/camera/detect";

const functionTabs = [
  {
    key: "single",
    name: "单图检测",
    desc: "快速识别一张图片",
    icon: Picture,
    accept: "image/*",
    multiple: false,
  },
  {
    key: "batch",
    name: "批量检测",
    desc: "一次处理多张图片",
    icon: Plus,
    accept: "image/*",
    multiple: true,
  },
  {
    key: "folder",
    name: "摄像头实时检测",
    desc: "实时检测",
    icon: Folder,
    accept: "image/*",
    multiple: true,
  },
  {
    key: "video",
    name: "视频检测",
    desc: "上传视频自动分析",
    icon: Monitor,
    accept: "video/*",
    multiple: false,
  },
];

const handleTabClick = async (key) => {
  activeTab.value = key;
  
  // 等待DOM更新后再触发文件选择
  await nextTick();
  
  // 单图和批量检测：手动触发文件选择
  if (key === "single" && singleInputRef.value) {
    singleInputRef.value.click();
  } else if (key === "batch" && batchInputRef.value) {
    batchInputRef.value.click();
  }
};

const handleFileChange = async (event, tabKey) => {
  event.stopPropagation();
  event.preventDefault();

  activeTab.value = tabKey;

  const files = event.target.files;

  if (!files || files.length === 0) {
    return;
  }

  if (tabKey === "single") {
    await performSingleDetection(files[0]);
  }

  if (tabKey === "batch") {
    await performBatchDetection(files);
  }

  // folder 和 video 已在面板中处理，此处不再处理

  setTimeout(() => {
    event.target.value = "";
  }, 0);
};

const startCamera = async () => {
  try {
    isConnecting.value = true;

    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: "user"
      }
    });

    videoRef.value.srcObject = cameraStream;

    await new Promise((resolve) => {
      videoRef.value.onloadedmetadata = () => {
        videoRef.value.play();
        resolve();
      };
    });

    cameraWs = new WebSocket(WS_URL);

    cameraWs.onopen = () => {
      console.log("WebSocket连接已建立");
      isStreaming.value = true;
      isConnecting.value = false;
      ElMessage.success("摄像头已开启，开始实时检测");
      startDetection();
    };

    cameraWs.onmessage = (event) => {
      const result = JSON.parse(event.data);
      handleDetectionResult(result);
    };

    cameraWs.onerror = (error) => {
      console.error("WebSocket错误:", error);
      ElMessage.error("WebSocket连接错误");
    };

    cameraWs.onclose = () => {
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
    if (!isStreaming.value || !cameraWs || cameraWs.readyState !== WebSocket.OPEN) {
      return;
    }

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const frameData = canvas.toDataURL("image/jpeg", 0.8).split(",")[1];

    cameraWs.send(JSON.stringify({
      frame: frameData,
      model_name: selectedModel.value
    }));

    frameCount++;
    const now = Date.now();
    if (now - lastFpsTime >= 1000) {
      fps.value = frameCount;
      frameCount = 0;
      lastFpsTime = now;
    }

    setTimeout(() => {
      cameraAnimationId = requestAnimationFrame(sendFrame);
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

  if (result.annotated_frame) {
    annotatedImage.value = `data:image/jpeg;base64,${result.annotated_frame}`;
  }

  currentBoxes.value = result.boxes || [];
  totalObjects.value += result.total_objects || 0;
  totalFrames.value++;
  latency.value = Math.round(result.detection_time * 1000);
};

const stopCamera = () => {
  isStreaming.value = false;

  if (cameraAnimationId) {
    cancelAnimationFrame(cameraAnimationId);
    cameraAnimationId = null;
  }

  if (cameraWs) {
    cameraWs.close();
    cameraWs = null;
  }

  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }

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

const performSingleDetection = async (file) => {
  const loading = ElLoading.service({
    lock: true,
    text: "正在检测中...",
    background: "rgba(0, 0, 0, 0.7)",
  });
  
  try {
    isDetecting.value = true;
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_name", selectedModel.value);
    
    originalImage.value = URL.createObjectURL(file);
    detectionResult.value = null;
    resultImage.value = null;
    
    const response = await detectSingleImage(formData);
    console.log("检测响应:", response);
    
    if (response.success && response.data) {
      detectionResult.value = response.data;
      // 构建完整的图片 URL
      resultImage.value = `http://localhost:8000${response.data.result_image_url}`;
      ElMessage.success(`检测成功！发现 ${response.data.total_objects} 个目标`);
    } else {
      ElMessage.error(response.message || "检测失败");
    }
  } catch (error) {
    console.error("检测错误:", error);
    ElMessage.error(error.response?.data?.detail || "检测失败，请稍后重试");
  } finally {
    isDetecting.value = false;
    loading.close();
  }
};
const performBatchDetection = async (files) => {
  const loading = ElLoading.service({
    lock: true,
    text: `正在批量检测 ${files.length} 张图片...`,
    background: "rgba(0, 0, 0, 0.7)",
  });

  try {
    isDetecting.value = true;

    const formData = new FormData();

    Array.from(files).forEach((file) => {
      formData.append("files", file);
    });

    formData.append("model_name", selectedModel.value);

    originalImage.value = null;
    resultImage.value = null;
    detectionResult.value = null;
    batchResults.value = [];

    const response = await detectBatchImages(formData);
    console.log("批量检测响应:", response);

    if (response.success && response.data) {
      batchResults.value = response.data;

      const firstSuccess = response.data.find((item) => item.success && item.data);

      if (firstSuccess) {
        detectionResult.value = firstSuccess.data;
        originalImage.value = `http://localhost:8000${firstSuccess.data.image_url}`;
        resultImage.value = `http://localhost:8000${firstSuccess.data.result_image_url}`;
      }

      ElMessage.success(`批量检测完成，共处理 ${response.data.length} 张图片`);
    } else {
      ElMessage.error(response.message || "批量检测失败");
    }
  } catch (error) {
    console.error("批量检测错误:", error);
    ElMessage.error(error.response?.data?.detail || "批量检测失败，请稍后重试");
  } finally {
    isDetecting.value = false;
    loading.close();
  }
};

const handleVideoChange = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;

  const loading = ElLoading.service({
    lock: true,
    text: "正在上传并检测视频，请稍候...",
    background: "rgba(0, 0, 0, 0.7)",
  });

  try {
    isDetecting.value = true;
    videoResult.value = null;
    videoProgress.value = 0;
    videoCurrentFrame.value = 0;
    videoTotalFrames.value = 0;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model_name", selectedModel.value);

    // 简单的加载动画，不模拟具体进度
    let progressTick = 0;
    const progressInterval = setInterval(() => {
      progressTick++;
      // 每 2 秒更新一次加载提示
      if (progressTick % 4 === 0) {
        loading.setText("正在逐帧分析视频，请稍候...");
      }
    }, 500);

    const response = await detectVideo(formData);

    clearInterval(progressInterval);
    videoProgress.value = 100;

    if (response.success && response.data) {
      videoResult.value = response.data;
      videoTotalFrames.value = response.data.total_frames || 0;
      ElMessage.success(`视频检测完成！共 ${response.data.total_frames} 帧，检测到 ${response.data.total_objects} 个目标`);
    } else {
      ElMessage.error(response.message || "视频检测失败");
    }
  } catch (error) {
    console.error("视频检测错误:", error);
    const errorMsg = error.response?.data?.detail || error.message || "视频检测失败，请稍后重试";
    ElMessage.error(errorMsg);
  } finally {
    isDetecting.value = false;
    loading.close();
    event.target.value = "";
  }
};

const showBatchResult = (item) => {
  if (!item || !item.data) {
    return;
  }

  detectionResult.value = item.data;
  originalImage.value = `http://localhost:8000${item.data.image_url}`;
  resultImage.value = `http://localhost:8000${item.data.result_image_url}`;
};

const handleRedetect = () => {
  if (singleInputRef.value) {
    singleInputRef.value.click();
  }
};
</script>

<style scoped>
.detection-page {
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

.model-selector {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 10;
}

.function-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.function-tab {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background-color: #ffffff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.hidden-input {
  display: none;
}

.function-tab:hover {
  background-color: var(--primary-light);
}

.function-tab.active {
  background-color: var(--primary-light);
  border-color: var(--primary-color);
}

.tab-icon {
  font-size: 18px;
  color: var(--primary-color);
  margin-right: 12px;
  flex-shrink: 0;
}

.tab-content {
  display: flex;
  flex-direction: column;
}

.tab-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
}

.tab-desc {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
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

.result-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.toolbar .el-button {
  border-radius: 6px;
  padding: 6px 14px;
}

.toolbar .el-button.active {
  background-color: var(--primary-light);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.image-compare {
  display: flex;
  gap: 16px;
  height: 320px;
}

.image-card {
  flex: 1;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f9fafb;
  display: flex;
  align-items: center;
  justify-content: center;
}

.compare-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-image {
  text-align: center;
  color: #999;
}

.placeholder-image .el-icon {
  margin-bottom: 8px;
}

.image-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.5);
  color: #ffffff;
  font-size: 13px;
}

.detection-mark {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detection-mark::after {
  content: "✓";
  color: #ffffff;
  font-size: 18px;
  font-weight: bold;
}

.right-panel {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
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

.result-card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 16px;
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
  margin-bottom: 4px;
}

.empty-desc {
  font-size: 13px;
  color: var(--text-secondary);
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

.diagnosis-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  flex: 1;
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
}

.batch-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.batch-item {
  padding: 10px 12px;
  background-color: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.batch-item:hover {
  background-color: var(--primary-light);
  border-color: var(--primary-color);
}

.batch-filename {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  word-break: break-all;
}

.batch-count {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.camera-panel {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
}

.camera-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  align-items: center;
}

.camera-content {
  display: flex;
  gap: 24px;
}

.camera-left {
  flex: 1;
}

.camera-right {
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.video-container {
  position: relative;
  width: 100%;
  background-color: #000;
  border-radius: 12px;
  overflow: hidden;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.canvas-element {
  display: none;
}

.annotated-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--text-secondary);
}

.placeholder p {
  margin-top: 16px;
  font-size: 14px;
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
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--primary-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.video-panel {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 24px;
  min-height: 400px;
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.video-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: var(--text-secondary);
}

.video-placeholder p {
  margin-top: 16px;
  font-size: 14px;
}

.video-hint {
  font-size: 12px !important;
  color: var(--text-secondary);
  margin-top: 8px !important;
}

.video-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.video-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
}

.progress-text {
  margin-top: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.video-result {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.video-info {
  display: flex;
  gap: 24px;
}

.info-card {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 8px;
}

.info-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.video-player {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.result-video {
  width: 100%;
  max-width: 800px;
  border-radius: 12px;
  background-color: #000;
}

.video-label {
  margin-top: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}

.hidden-input {
  display: none;
}
</style>